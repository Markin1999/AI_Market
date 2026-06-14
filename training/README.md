# training/ — le due IA: vedere (occhio) e prevedere (predittore)

Questa cartella è il **cervello che impara**, separato dalla pipeline dati. Contiene **due IA distinte** che condividono `config.py` e `data/`. Qui sotto, in linguaggio chiaro, **cosa costruiamo, perché e come**.

> **Stato:** due IA. L'**occhio** ([occhio/](occhio/)) — Stadio 1, *Vedere* — è **fatto e validato** (3 test passati). Il **predittore** ([predittore/](predittore/)) — Stadio 2, *Prevedere* — è **da costruire** (Fase 3). Questo documento è la **visione**; il **come tecnico** dell'occhio è in **[occhio/COME_FUNZIONA_LOCCHIO.md](occhio/COME_FUNZIONA_LOCCHIO.md)**. Roadmap: [Fase 2](../Regole/Roadmap%20delle%20fasi/Fase2_Roadmap.md) · [Fase 3](../Regole/Roadmap%20delle%20fasi/Fase3_Roadmap.md).

---

## Cosa legge, cosa usa, cosa NON tocca

- **Legge** il database `data/raw/market.duckdb` — le candele con i 45 indicatori già calcolati dalla pipeline.
- **Usa** `shared/` per la configurazione (titoli, settori) e il calcolo indicatori — *una copia sola*, condivisa con la pipeline, così non divergono mai.
- **NON** scarica da Polygon, **non** usa API key, **non** tocca la pipeline dati.
- **Produce** in `models/` (alla root): l'occhio addestrato + la libreria dei pattern in `models/pattern_memory/`.

---

## Il piano in tre stadi (la visione)

Il bambino impara nello stesso ordine in cui imparerebbe un bambino vero. Un senso alla volta. Non si va avanti finché lo stadio corrente non funziona in modo misurabile.

| Stadio | Nome | Cosa impara, in parole semplici |
|---|---|---|
| **1** | **Vedere** | Legge **tutte le candele di tutti gli anni** e costruisce una **libreria di grafici** — un archivio di forme che sa sia **riconoscere** sia **ricostruire**. Saper ridisegnare una forma è la prova che l'ha capita. |
| **2** | **Associare** | Usa la libreria **+ la lista dei 45 indicatori e dei pattern** per riconoscere le situazioni e **decidere se investire**. Qui arriva la ricompensa: giusto o sbagliato. |
| **3** | **Contestualizzare** | Costruisce i **grafici di settore**, capisce **in giornata quale settore va meglio** e le relazioni tra settori ("se sale il tech, cosa fa l'energia?"), così sa **in che settore cercare i pattern e investire**. |

**Questa cartella, per ora, costruisce lo Stadio 1.** Gli stadi 2 e 3 si progettano quando il precedente è solido.

> **Nota sul multi-timeframe (futuro).** L'idea di partire dai dati *al secondo* e costruire grafici da 1 minuto, 15 minuti, ecc. arriva più avanti: serve prima procurarsi i dati al secondo. **Per ora lavoriamo con i 15 minuti** che già abbiamo — è la base giusta per insegnargli a vedere.

---

## Stadio 1 — Vedere

### L'obiettivo: due risultati

Lo Stadio 1 produce **due cose**, non una:

1. **L'occhio** — capace di leggere *qualsiasi* finestra di grafico e trasformarla in una "firma" che ne descrive la struttura.
2. **La libreria di grafici** (`models/pattern_memory/`) — l'archivio di forme fondamentali che l'occhio ha scoperto da solo, una cartella che puoi aprire, guardare e **arricchire a mano** coi pattern dei libri.

Nessuna previsione, nessuna ricompensa ancora. Prima di tutto: saper guardare.

### Come guarda i dati — un giorno alla volta

Il bambino non guarda 5 anni schiacciati in un grafico solo. Guarda un **pezzo alla volta**, come un trader guarda lo schermo: le ultime ore/giorni, poi scorre.

Pensa a un **libro**: lo leggi una pagina alla volta, ma leggi **tutto il libro**.

- **La finestra = 1 giorno (64 candele)** → la *pagina* che guarda in un colpo d'occhio.
- **Tutti i 5 anni di tutti i 66 titoli** → il *libro intero* che legge, pagina dopo pagina.

```
Storia completa di un titolo (5 anni)  ───────────────────────────►
                                       [giorno][giorno][giorno]...
                                        ↑pagina1
                                               ↑pagina2
                                                      ↑pagina3   ...milioni di pagine
                                        (poi tutti gli altri 65 titoli)
```

Tagliamo tutta la storia in **milioni di finestre da un giorno** (≈ 3,5 milioni in tutto) e gliele facciamo scorrere davanti una dopo l'altra — le vede **tutte**, e le ripassa più volte.

- **Da quanto impara:** da tutto. Ogni candela di ogni anno di ogni titolo diventa una pagina.
- **Quanto vede in un colpo d'occhio:** un giorno. È solo la dimensione dello sguardo.

> Perché un giorno? Perché una *forma* (un trend, un supporto, un breakout) è una cosa locale: succede in ore o giorni, non in 5 anni. 64 candele = un giorno intero di mercato (08:00–23:45, extended hours inclusi). La finestra si può **allargare** (2 giorni, una settimana) se serve più contesto.

### Cosa vede in ogni candela — la forma + i 45 sensi

Ogni candela non è solo 5 numeri (apertura, massimo, minimo, chiusura, volume). Porta con sé anche i suoi **45 indicatori** già calcolati — i suoi "sensi". Quindi una candela ≈ **50 numeri**, e una finestra di un giorno = 64 candele × ~50 numeri.

Vogliamo che, guardando un giorno, veda **la forma e tutti i sensi insieme**.

**Il problema: i numeri non sono confrontabili.** Vivono su scale diversissime —

| Dato | Scala tipica |
|---|---|
| RSI | 0 – 100 |
| MACD | piccolo (±2) |
| OBV (volume cumulato) | **milioni** |
| Prezzo | ~$185 |
| Pattern candele | 100 / 0 / -100 |

Se li diamo grezzi, i numeri grandi **schiacciano** i piccoli: l'OBV da milioni cancellerebbe l'RSI. L'occhio vedrebbe solo il volume.

**La soluzione (il "cosa farcene" dei 45 dati) — tre mosse:**

1. **Normalizzare** — riportare ogni dato alla stessa scala (es. tutti tra -1 e +1). Così RSI, MACD e OBV pesano uguale e sono confrontabili. Una salita del 2% di NVDA e una di KO diventano identiche: conta la forma, non il titolo né il prezzo assoluto.
2. **Raggruppare per famiglia** — momentum, trend, volatilità, volume, Ichimoku — come già nel catalogo. Ordine, non caos.
3. **I pattern come bandierine** — sono già 100/0/-100: restano segnali "acceso/spento" che si accendono nel giorno.

> **Filosofia.** Li mettiamo **tutti dentro, normalizzati**, e lasciamo che sia il risultato a dire quali contano davvero — non lo decidiamo noi in anticipo. Se in addestramento l'occhio fatica con troppi dati, si parte da un gruppo ridotto e si aggiungono. Il mercato decide.

### Come impara a vedere — prima ricopiare, poi la libreria

Procediamo **a piccoli passi** (gattona prima di camminare):

**Passo A — Imparare a ricopiare.** Prima costruiamo una rete semplice (un *autoencoder*) che fa una cosa sola: **guarda una finestra e prova a ridisegnarla**. Comprime il giorno in pochi numeri (la firma) e poi lo ricostruisce. Se ci riesce bene, vuol dire che ha capito la struttura. È facile da controllare e correggere.

**Passo B — Costruire la libreria.** Quando sa ricopiare, aggiungiamo un **dizionario di forme** (il "codebook"): invece di una firma libera, l'occhio sceglie la forma più simile da un archivio di forme tipiche. È il salto da autoencoder a **VQ-VAE**. Quell'archivio **è** la libreria di grafici — la "memoria visiva" del sistema.

```
finestra (1 giorno)  →  [ OCCHIO: comprime ]  →  firma  →  [ sceglie la forma dalla libreria ]
                                                                        │
       ricostruzione (ridisegna il giorno)  ◄──────────────────────────┘
```

Il risultato è un **occhio** che trasforma qualsiasi giorno di grafico in una firma, e una **libreria** di forme leggibile e arricchibile.

### La libreria dei pattern — un archivio che cresce

```
models/pattern_memory/
  codebook.npy           ← il dizionario interno (scoperto dai dati)
  pattern_000.npy        ← forma 0: laterale
  pattern_001.npy        ← forma 1: breakout rialzista
  pattern_002.npy        ← forma 2: trend ribassista
  ...
  book_testa_spalle.npy  ← aggiunto a mano da un libro di analisi tecnica
  book_doppio_massimo.npy
```

Ogni pattern è un vettore di numeri, ma si può **visualizzare come grafico**. Puoi aprire la cartella, vedere cosa ha imparato, e **aggiungere pattern dai libri**. Non diventano regole rigide: se nei dati reali quel pattern ha anticipato movimenti, il sistema lo userà; se no, lo ignorerà. Il mercato resta il giudice.

### Come sapremo che "ci vede" davvero — i 3 test

1. **Ricostruzione su dati mai visti.** Si tengono da parte alcuni mesi che il sistema non ha mai visto. Se riesce a ricopiarli bene, ha imparato strutture *generali*, non li ha memorizzati a memoria.
2. **Coerenza tra titoli diversi (il test chiave).** Si mettono le firme di migliaia di finestre su una mappa. Se la salita di NVDA finisce **vicino** alla salita di KO — titoli diversissimi, stessa forma — allora vede la *struttura*, non il titolo.
3. **Stabilità nel tempo.** Una salita del 2021 e una del 2024 devono finire vicine sulla mappa: il mercato cambia, le forme di fondo restano.

Quando tutti e tre passano in modo stabile, lo Stadio 1 è completo.

---

## La struttura delle cartelle

Due IA separate, con i pezzi **condivisi** sopra. Ogni componente è isolato, così si aggiorna senza buttare via il resto.

```
training/
├── README.md            # questo file (visione d'insieme)
├── config.py            # CONDIVISO — tutti i numeri (finestra=64, firma=32, dizionario=256...)
├── data/                # CONDIVISO — preparazione dati
│   ├── windows.py       #   taglia la storia in finestre da un giorno (scorrevoli)
│   └── normalize.py     #   porta forma + indicatori alla stessa scala
│
├── occhio/              # IA #1 — VEDERE (fatta, validata)
│   ├── COME_FUNZIONA_LOCCHIO.md  # la guida tecnica dell'occhio
│   ├── architecture/    #   encoder, decoder, quantizer (dizionario), vqvae
│   ├── train.py         #   addestra l'occhio (log in logs/training.log)
│   ├── evaluate.py      #   i 3 test (ricostruzione, mappa 2D, stabilità)
│   ├── pattern_memory.py #  disegna la libreria in models/pattern_memory/
│   └── mostra_*.py      #   visualizzazioni (finestra→forma, originale vs copia)
│
└── predittore/          # IA #2 — PREVEDERE (da costruire, Fase 3)
    ├── README.md        #   cosa farà + la lezione della sonda
    └── sonda_predittiva.py  # la sonda: forma da sola ≈ 50% (baseline da battere)
```

I **modelli addestrati** e la **libreria** vanno in `models/` (alla root): qui dentro c'è solo il **codice**.

---

## I passi concreti (per arrivarci)

1. **Ambiente** — struttura delle cartelle, librerie (PyTorch, scikit-learn per le mappe 2D).
2. **Dati** — tagliare la storia in finestre da un giorno, normalizzare, dividere in *train / validation / test* (il test è un periodo **futuro** rispetto al training, mai una scelta a caso).
3. **Occhio — Passo A** — addestrare l'autoencoder a ricopiare le finestre.
4. **Occhio — Passo B** — aggiungere il dizionario (codebook) → VQ-VAE → nasce la libreria.
5. **Verifica** — i 3 test + visualizzare le forme scoperte.
6. **Arricchire** — aggiungere pattern dai libri alla libreria.

Dettaglio narrativo completo nella [roadmap della Fase 2](../Regole/Roadmap%20delle%20fasi/Fase2_Roadmap.md).

---

## Riepilogo delle decisioni prese

| Decisione | Scelta | In breve |
|---|---|---|
| **Finestra** | 1 giorno = **64 candele** | Il "colpo d'occhio". Si può allargare dopo. |
| **Da cosa impara** | **Tutte** le finestre di tutti gli anni e titoli (≈3,5M) | Vede tutto il "libro", una pagina alla volta. |
| **Cosa vede per candela** | Forma (OHLC+volume) **+ 45 indicatori** | Tutto insieme, perché i sensi sono già calcolati. |
| **Cosa farne dei 45 dati** | **Normalizzare** alla stessa scala + raggruppare + pattern come bandierine | Senza, i numeri grandi schiacciano i piccoli. |
| **Come parte l'occhio** | Prima **ricopiare** (autoencoder), poi la **libreria** (VQ-VAE) | Un passo alla volta, facile da correggere. |
| **Ricompensa** | Nessuna (arriva allo Stadio 2) | Prima vedere, poi associare e investire. |

---

## Cosa viene dopo lo Stadio 1

- **Stadio 2 — Associare/investire:** sopra l'occhio si aggiunge una "testa" che, vista una forma, decide se il prezzo salirà o scenderà. Qui entrano **la tua lista** (indicatori + pattern) e la **ricompensa**. Soglia minima di successo: accuracy direzionale **> 53%** su dati mai visti.
- **Stadio 3 — Settori:** grafici di settore, capire **in giornata quale settore va meglio** e le relazioni tra settori, per scegliere **dove** investire. (Da progettare: anche un *riassunto di settore* da dare al sistema accanto al singolo titolo.)
- **Multi-timeframe** (1 min / 15 min da dati al secondo): più avanti, quando avremo i dati al secondo.

---

## Stato e prossimo passo

**Stato:** **Stadio 1 (occhio) completato e validato** — i 3 test sono passati (ricostruzione out-of-sample, coerenza tra titoli, stabilità nel tempo). L'occhio + la libreria sono in `models/`. Dettaglio tecnico e risultati in [occhio/COME_FUNZIONA_LOCCHIO.md](occhio/COME_FUNZIONA_LOCCHIO.md).

**Prossimo passo:** la **Fase 3** — il **predittore** ([predittore/](predittore/)): la testa che, da firma + indicatori, prevede su/giù. La sonda ha già fissato il baseline (forma da sola ≈ 50%, da battere). Vedi [roadmap Fase 3](../Regole/Roadmap%20delle%20fasi/Fase3_Roadmap.md).

---

*AI Market Predictor · training · Stadio 1 (occhio) fatto · Stadio 2 (predittore) in arrivo. Vedi [roadmap Fase 2](../Regole/Roadmap%20delle%20fasi/Fase2_Roadmap.md), [roadmap Fase 3](../Regole/Roadmap%20delle%20fasi/Fase3_Roadmap.md) e [documento principale](../Regole/Documento_Principale/README.md).*
