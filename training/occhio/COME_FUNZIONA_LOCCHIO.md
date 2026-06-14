# 👁️ Come funziona l'Occhio — il primo modello di addestramento (Stadio 1)

> **A chi serve questo documento.** A chiunque apra il progetto — te, un collaboratore, o **Claude stesso** in una sessione futura — per capire **esattamente** come funziona il primo modello: cosa fa ogni funzione, com'è fatta la rete neurale, come impara, e — onestamente — **rischi, pregi e come migliorarlo**.
>
> Questo file spiega il **come (tecnico)**. La **visione (il perché)** è in [README.md](../README.md). La roadmap completa è in [Fase2_Roadmap.md](../../Regole/Roadmap%20delle%20fasi/Fase2_Roadmap.md).

---

## In una frase

L'**occhio** è una rete neurale (un **VQ-VAE**) che impara a guardare **un giorno di mercato alla volta** e a fare due cose:
1. **ridisegnarlo** (se sa ricopiarlo, vuol dire che ne ha capito la forma);
2. **assegnarlo a una "forma"** scelta da un **dizionario di 256 forme tipiche**.

Da quel dizionario nasce la **libreria dei pattern** — l'archivio di forme del mercato che il sistema userà nello Stadio 2 per decidere se investire.

**Importante:** questo modello **non prevede** e **non guadagna** ancora. Impara solo a *vedere*. È la fondazione.

---

## È "vera IA"?

Sì, senza giri di parole. Il ciclo in [train.py](train.py) è il **ciclo di addestramento canonico** di una rete neurale — la stessa matematica (discesa del gradiente, backpropagation) con cui si addestrano i modelli grandi. Il **VQ-VAE** è un'architettura pubblicata (DeepMind, 2017), la stessa famiglia usata in modelli di immagini e audio. La differenza dai modelli enormi è di **scala e compito**, non di natura.

---

## 1. Il viaggio di un dato — funzione per funzione

Seguiamo **una singola finestra** dal database fino all'occhio.

```
DATABASE → load_clean_series → CandleWindows → __getitem__ + Normalizer → DataLoader → MODELLO
 (candele)   (pulisce)          (taglia+divide)   (fa la "forma")          (a blocchi)   (impara)
```

### 1.1 — Leggere dal database · `load_clean_series` ([windows.py:35](../data/windows.py#L35))
```sql
SELECT ts, open, high, ... FROM candles WHERE ticker = ? ORDER BY ts
```
- **`ORDER BY ts`** → le candele escono **in ordine di tempo**, mai mescolate.
- **`.dropna(...)`** → scarta le righe di *warmup* (i primi giorni in cui gli indicatori sono NaN: l'EMA a 200 candele non esiste finché non hai 200 candele prima).
- **Risultato:** la storia pulita e ordinata di **un** titolo.

### 1.2 — Tagliare in finestre + dividere train/val/test · `CandleWindows.__init__` ([windows.py:56](../data/windows.py#L56))
- Carica ogni titolo in memoria come array di numeri (`self.series`).
- **Non salva le finestre** (sarebbero decine di GB): salva solo *dove iniziano* — `self.index` è una lista di coppie `(titolo, start)`, dei semplici "segnalibri". Per questo milioni di finestre stanno in RAM.
- Per ogni inizio, guarda la **data dell'ultima candela** e con `_split_of` ([:44](../data/windows.py#L44)) decide: **train** (≤ 2025-06-30) / **val** (≤ 2025-12-31) / **test** (dopo). Il test è un periodo **futuro**, mai una scelta a caso: così si misura su un mercato mai visto.

### 1.3 — ⭐ Fare la "forma" · `__getitem__` ([windows.py:86](../data/windows.py#L86)) + `Normalizer` ([normalize.py:41](../data/normalize.py#L41))
Quando l'addestramento chiede *"dammi la finestra n°i"*:
```python
def __getitem__(self, i):
    t, start = self.index[i]                  # quale titolo, da dove
    arr = self.series[t][start:start + 64]    # taglia 64 candele × 47 numeri GREZZI
    return torch.from_numpy(self.norm(arr))   # → normalizza → la FORMA (64, 47)
```
Il `Normalizer` è il cuore: trasforma i numeri grezzi in **forma confrontabile**, una regola per famiglia ([normalize.py:43-59](../data/normalize.py#L43-L59)):

| Famiglia | Regola | Perché |
|---|---|---|
| Prezzo (OHLC, medie, bande…) | `(x − media_close) / dev_close` | toglie il prezzo assoluto: **resta solo la forma**. Una salita di NVDA e una di KO diventano identiche |
| Volume | z-score | numeri enormi → scala normale |
| RSI/Stoch (0–100) | `x/50 − 1` | porta a −1..+1 |
| Williams (−100..0), pattern… | regole simili | tutto alla **stessa scala** |

> **Questo è "trasformare il dato in forma":** spogliare i numeri dal prezzo e dalla grandezza, lasciando solo l'**andamento**, comparabile tra aziende diverse. Ogni finestra si normalizza **da sola** → funziona su qualsiasi titolo, anche mai visto, senza ri-tarature.

### 1.4 — Raggruppare e mescolare · `DataLoader` ([train.py:62](train.py#L62))
```python
DataLoader(train_ds, batch_size=256, shuffle=True)
```
- **`batch_size=256`** → 256 finestre alla volta (un *blocco*/*batch*). Si impara a blocchi, non una alla volta (più veloce e più stabile).
- **`shuffle=True`** → le mescola, così l'occhio non vede sempre lo stesso ordine.

---

## 2. Il modello IA — pezzo per pezzo

Tre componenti in fila, definiti in [architecture/](architecture/):

```
finestra (64×47) ─► ENCODER ─► firma (32 numeri) ─► DIZIONARIO ─► forma scelta ─► DECODER ─► ricostruzione (64×47)
                    [occhio]                         [codebook]                    [ridisegna]
```

### 2.1 — Encoder: l'occhio che comprime · [encoder.py](architecture/encoder.py)
Due strati **convoluzionali 1D** (scorrono lungo il tempo — ideali per le forme dei grafici) e poi uno strato che schiaccia tutto in una **firma** di 32 numeri:
```
Conv1d(47 → 64,  k=4, s=2)   # 64 passi temporali → 32
Conv1d(64 → 128, k=4, s=2)   # 32 → 16
Flatten + Linear(128×16 → 32)  # → firma da 32 numeri
```

### 2.2 — VectorQuantizer: il dizionario · [quantizer.py](architecture/quantizer.py)
Prende la firma e la **aggancia alla forma più vicina** tra le 256 del dizionario (come arrotondare una parola alla più simile di un vocabolario limitato). Produce:
- `zq` = la forma scelta, `idx` = **quale** delle 256 (un numero 0–255),
- una **loss del dizionario** che, allenando, sposta le 256 forme per descrivere meglio i grafici reali,
- un "trucco" (*straight-through*) per far passare la correzione attraverso lo scalino.

> **Punto chiave:** ogni giorno viene ridotto a **UNA sola** voce del dizionario (1 fra 256, ≈ 8 bit). È una compressione **estrema** — ottima per la *libreria* (ogni giorno = una forma, perfetto per "trovami tutti i giorni forma #47"), ma **limita** la fedeltà del ridisegno (vedi Rischi).

### 2.3 — Decoder: ridisegna · [decoder.py](architecture/decoder.py)
Lo specchio dell'encoder: dalla forma scelta risale, con due convoluzionali "al contrario", fino a riottenere una finestra `(64, 47)`.

### 2.4 — VQVAE: il tutto assemblato · [vqvae.py](architecture/vqvae.py)
```python
def forward(self, x):                 # x: (B, 64, 47)
    z  = self.encoder(...)            # firma
    zq, vq_loss, idx = self.quantizer(z)   # forma del dizionario
    recon = self.decoder(zq)          # ridisegno
    return recon, vq_loss, idx
```

**I numeri del modello:** ~**231.000 parametri** · firma da **32** numeri · dizionario da **256** forme · finestra **64×47**.

---

## 3. Come impara — epoche e ciclo di addestramento

### Cos'è un'epoca
> **Un'epoca = un giro completo su TUTTE le finestre.** Con 2,78 milioni di finestre e blocchi da 256 → **10.888 blocchi = 1 epoca**. Ne facciamo 12: l'occhio rivede tutto 12 volte (come rileggere un libro 12 volte: ogni passata capisce di più).

### Il ciclo · [train.py:71-95](train.py#L71-L95)
Per **ogni blocco**:
```python
recon, vq_loss, idx = model(x)      # 1. ridisegna le 256 forme + sceglie dal dizionario
recon_loss = loss_fn(recon, x)      # 2. quanto ha sbagliato la copia? (errore di ricopiatura)
loss = recon_loss + vq_loss         #    errore copia + errore dizionario
loss.backward()                     # 3. calcola COME correggersi (backpropagation)
opt.step()                          # 4. si corregge un pochino (discesa del gradiente)
```
A fine epoca scrive nel **log** l'errore medio + quante forme del dizionario ha usato. **L'errore che scende epoca dopo epoca = sta imparando.**

### Il log dal vivo
Tutto va in **`logs/training.log`** in tempo reale. Per seguirlo:
```bash
tail -f logs/training.log
```

---

## 4. Come si lancia

| Comando | Cosa fa |
|---|---|
| `python training/occhio/train.py --model vqvae --tickers 10 --epochs 6` | **Test veloce** (10 titoli, ~8 min) |
| `python training/occhio/train.py --model vqvae` | **Allenamento completo** (66 titoli, ~1,5 h) |
| `python training/occhio/train.py --model auto` | Solo autoencoder, senza dizionario (Passo A) |
| `python training/occhio/pattern_memory.py --tickers 10` | Tira fuori la **libreria** (disegna le forme) → `models/pattern_memory/libreria.html` |
| `python training/occhio/mostra_finestra.py` | Vedi una finestra reale che diventa "forma" |
| `python training/occhio/mostra_ricostruzione.py` | Vedi originale vs copia dell'occhio |

I comandi si lanciano **dalla root del progetto**.

---

## 5. I risultati reali finora (onesti)

| Prova | Errore copia | Dizionario usato | Note |
|---|---|---|---|
| Test 10 titoli, 6 epoche | 0.50 → **0.088** (solo autoencoder) | — | il ridisegno è ottimo *senza* dizionario |
| Test 10 titoli, 6 epoche (VQ-VAE) | 0.50 → **0.37** | 73 → 33 → **48** /256 | col dizionario il ridisegno peggiora (atteso), forme crollate e poi risalite |
| **Completo 66 titoli** (in corso) | epoca 1: **0.40** | epoca 1: **69**/256 | parte già meglio del test (più dati) |

**Lettura onesta:** il *meccanismo* funziona. La *qualità* è una prima bozza: ridisegno mediocre e dizionario usato al ~27%. Il giudizio vero arriva dai **3 test** (sezione 9).

---

## 6. ⚠️ I RISCHI (onestà totale)

| Rischio | Cos'è | Quanto preoccupa |
|---|---|---|
| **Codebook collapse** | Il VQ-VAE usa solo una frazione delle 256 forme (ora ~27%). Tendenza nota di questi modelli. | Medio — risolvibile (sez. 8) |
| **Ridisegno mediocre (0.37)** | In parte *per scelta*: comprimiamo un giorno in **una sola** forma (sez. 2.2). Ottimo per la libreria, limitante per il ridisegno. | Basso/atteso |
| **Modello forse troppo piccolo** | 231k parametri, firma da 32: potrebbe non bastare a catturare tutta la varietà. | Da verificare coi test |
| **Overfitting** | Imparare a memoria invece che la struttura. | Lo intercetta il **test su dati futuri** |
| **🎯 Prevedere il mercato è difficile** | Questo è il rischio vero del progetto, e vive nello **Stadio 2**, non qui. Nessun occhio, per quanto buono, garantisce di guadagnare. | Alto — ma è onestà, non un difetto di questo passo |
| **Dati limitati** | Solo 15 min, 5 anni, 66 titoli. | Basso ora, ampliabile |

### Limite onesto sui controlli
I controlli garantiscono che la **lettura** è corretta (forma giusta, niente NaN, ordine, scala). Che i **dati di partenza** siano giusti è un altro controllo — la pipeline e gli indicatori, già verificati a parte.

---

## 7. ✅ I PRO

- **È IA vera e standard** — VQ-VAE pubblicato, ciclo di training canonico, gira su GPU (MPS).
- **Giusta misura + iterazione veloce** — piccolo apposta: verifichi che tutto regge e impari cosa funziona in 1,5 h, non in giorni.
- **Modulare** — encoder, dizionario, decoder, dati: pezzi separati, si cambia uno senza rompere il resto.
- **Verificabile** — 3 test concreti dicono se "ci vede" davvero (sez. 9).
- **Scalabile senza riscrivere** — più titoli e più anni entrano da soli (legge tutti i titoli dal DB, normalizza per-finestra). Aggiungi dati, non rifai codice.
- **Generalizza** — l'occhio "vede" anche aziende mai viste, perché impara *forme*, non *nomi*.

---

## 8. 🔧 I MIGLIORAMENTI possibili (le leve)

In ordine, se i test dicono che serve più potenza:

1. **Firma più larga** (`SIGNATURE_DIM` 32 → 64/128) — più capacità di descrizione, ridisegno migliore.
2. **Più codici per finestra** (griglia invece di 1 sola voce) — migliora molto il ridisegno; cambia però la libreria (un giorno = sequenza di forme, non una sola).
3. **Modello più profondo** — più strati conv nell'encoder/decoder.
4. **Più epoche** — l'errore scendeva ancora a fine corsa.
5. **Anti-collapse del dizionario** — aggiornamento EMA dei codici, *restart* dei codici morti, abbassare il peso `beta` in [quantizer.py](architecture/quantizer.py).
6. **Dimensione dizionario** (`CODEBOOK_SIZE`) — su/giù secondo quante forme vengono davvero usate.
7. **Finestra più larga** (`WINDOW` 64 → 2 giorni/una settimana) — più contesto.
8. **+6 indicatori esclusi** (Parabolic SAR, Ichimoku proiezioni) — quando gestiamo i loro NaN ([config.py:67](../config.py#L67)).
9. **`num_workers` nel DataLoader** — caricamento dati più veloce (occhio alla RAM su Mac da 8 GB).

> Tutti **interruttori**, non riscritture. Si accendono **sulle prove reali**, non per paura.

---

## 9. Come sapremo che "ci vede" davvero — i 3 test · `evaluate.py`

1. **Ricostruzione su dati mai visti.** Ridisegna bene i mesi futuri tenuti da parte? → ha imparato strutture *generali*, non a memoria.
2. **Coerenza tra titoli (il test chiave).** Su una mappa 2D, la salita di NVDA finisce **vicino** alla salita di KO? → vede la *forma*, non il *titolo*.
3. **Stabilità nel tempo.** Una salita del 2021 e una del 2024 finiscono vicine? → le forme di fondo restano, anche se il mercato cambia.

Quando tutti e tre passano in modo stabile, lo **Stadio 1 è completo**.

---

## 10. Mappa dei file di `training/`

| File | Cosa fa |
|---|---|
| [config.py](../config.py) | **Tutti i numeri in un posto**: finestra, firma, dizionario, date di split, lista feature. |
| [data/windows.py](../data/windows.py) | Legge il DB, taglia in finestre, divide train/val/test. |
| [data/normalize.py](../data/normalize.py) | Porta forma + indicatori alla **stessa scala** (fa la "forma"). |
| [architecture/encoder.py](architecture/encoder.py) | L'occhio: comprime una finestra in una firma. |
| [architecture/quantizer.py](architecture/quantizer.py) | Il **dizionario** (codebook): aggancia la firma alla forma più vicina. |
| [architecture/decoder.py](architecture/decoder.py) | Ridisegna la finestra dalla forma. |
| [architecture/vqvae.py](architecture/vqvae.py) | Assembla `Autoencoder` (Passo A) e `VQVAE` (Passo B). |
| [train.py](train.py) | Il **ciclo di addestramento** (log live in `logs/training.log`). |
| [pattern_memory.py](pattern_memory.py) | Tira fuori e disegna la **libreria** in `models/pattern_memory/`. |
| [evaluate.py](evaluate.py) | I **3 test** (da completare). |
| [mostra_finestra.py](mostra_finestra.py) | Vede una finestra reale che diventa "forma". |
| [mostra_ricostruzione.py](mostra_ricostruzione.py) | Originale vs copia dell'occhio. |
| [README.md](../README.md) | La **visione** (il perché). Questo file è il **come**. |

Modelli e libreria prodotti vanno in `models/` (alla root): qui c'è solo **codice**.

---

## Glossario veloce

| Termine | In parole semplici |
|---|---|
| **Epoca** | Un giro completo su tutte le finestre. |
| **Batch / blocco** | Un gruppo di finestre (256) elaborate insieme. |
| **Firma** | I 32 numeri in cui l'encoder comprime un giorno. |
| **Codebook / dizionario** | Le 256 forme tipiche; ogni giorno ne sceglie una. |
| **Autoencoder** | Rete che impara a ricopiare (comprimere → ricostruire). |
| **VQ-VAE** | Autoencoder + dizionario di forme. |
| **Loss / errore** | Quanto ha sbagliato; si cerca di abbassarlo. |
| **Backpropagation** | Il calcolo di *come* correggersi. |
| **Discesa del gradiente** | Correggersi un pochino nella direzione giusta. |
| **Normalizzazione** | Portare numeri diversi alla stessa scala. |
| **Overfitting** | Imparare a memoria invece della struttura. |

---

*AI Market Predictor · Fase 2 · Stadio 1 — Vedere. Documento tecnico del primo modello. Visione in [README.md](../README.md), comandi in [readmeIstruzioniAvvio.md](../../readmeIstruzioniAvvio.md).*
