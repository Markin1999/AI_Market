# AI MARKET PREDICTOR
### Fase 2 — Training: Stadio 1 (Vedere) e Stadio 2 (Associare)
*Un documento per capire cosa stiamo costruendo, perché, e come ci arriviamo.*

> **Stato: IN CORSO.** La Fase 1 — Fondamenta è completata. Le decisioni dello Stadio 1 sono state prese (giugno 2026) e sono scritte anche, in versione operativa, nel [README di `training/`](../../training/README.md). Questo documento è la *storia*: il perché e il come.

---

## Prima di tutto: cosa cambia nella Fase 2

Nella Fase 1 abbiamo costruito il mondo. 3.508.585 candele, 45 indicatori calcolati su ognuna, database pulito, dashboard per esplorarlo. Il bambino ha la scacchiera, i pezzi, e ha visto com'è fatta.

Nella Fase 2 il bambino comincia a giocare.

Ma non in modo caotico. Segue la stessa progressione naturale di un bambino che impara: prima impara a *vedere* (Stadio 1), poi impara a *collegare quello che vede a quello che succede dopo* e a investire (Stadio 2), poi a *capire il contesto dei settori* (Stadio 3). Non si passa avanti finché il passo corrente non funziona in modo misurabile.

Tutto continua a girare in locale, sul Mac — esattamente come la Fase 1. Il server Hetzner entra solo quando il sistema dovrà girare H24 in autonomia, più avanti.

### I tre stadi, nel linguaggio di tutti i giorni

| Stadio | Nome | Cosa impara |
|---|---|---|
| **1** | **Vedere** | Legge tutte le candele di tutti gli anni e costruisce una **libreria di grafici** — un archivio di forme che sa **riconoscere** e **ricostruire**. |
| **2** | **Associare** | Usa la libreria **+ la lista dei 45 indicatori e dei pattern** per riconoscere le situazioni e **decidere se investire**. Qui arriva la ricompensa. |
| **3** | **Contestualizzare** | Costruisce i grafici **di settore**, capisce in giornata quale settore va meglio e come i settori si influenzano, per scegliere **dove** investire. |

Questo documento copre in dettaglio lo **Stadio 1** e dà una panoramica dello **Stadio 2**. Lo Stadio 3 (settori) si progetterà quando i primi due saranno solidi.

> **Multi-timeframe (futuro).** L'idea di partire dai dati *al secondo* e costruire grafici da 1 minuto, 15 minuti, ecc. arriva più avanti: serve prima procurarsi i dati al secondo. Per ora lavoriamo con i **15 minuti** che già abbiamo.

---

## Stadio 1 — Vedere

### L'obiettivo in una frase

Insegnare al sistema a riconoscere le **strutture** dei grafici — trend, supporti, pattern ricorrenti — senza ancora fare previsioni e senza ancora ricevere ricompensa. Prima di tutto, bisogna saper guardare.

Lo Stadio 1 produce **due cose**: l'**occhio** (sa leggere qualsiasi grafico e ridurlo a una "firma") e la **libreria di grafici** (l'archivio di forme che riconosce e sa ricostruire).

### Il parallelo con il bambino

Un neonato all'inizio vede solo macchie sfocate. Col tempo la corteccia visiva si organizza: prima i bordi, poi le forme, poi gli oggetti. Il bambino riconosce una palla *prima* di sapere a cosa serve. Il riconoscimento viene prima del significato.

Lo Stadio 1 costruisce la corteccia visiva del sistema per i grafici. Impara a distinguere "questa è una salita", "questo è un laterale", "qui c'è un supporto" — senza ancora sapere se sia un bene o un male per il trading. Quello arriva allo Stadio 2.

### Cosa "vede" il sistema — un giorno alla volta

Il bambino non guarda 5 anni schiacciati in un grafico solo. Guarda un **pezzo alla volta**, come un trader guarda lo schermo: le ultime ore o giorni, poi scorre.

Pensa a un **libro**: lo leggi una pagina alla volta, ma leggi *tutto* il libro.

- **La finestra = 1 giorno (64 candele)** → la *pagina* che guarda in un colpo d'occhio.
- **Tutti i 5 anni di tutti i 66 titoli** → il *libro intero* che legge, pagina dopo pagina.

Tagliamo tutta la storia in **milioni di finestre da un giorno** (≈ 3,5 milioni in tutto) e gliele facciamo scorrere davanti una dopo l'altra: le vede **tutte**, e le ripassa più volte.

- **Da quanto impara:** da tutto — ogni candela di ogni anno di ogni titolo diventa una pagina.
- **Quanto vede in un colpo d'occhio:** un giorno. È solo la dimensione dello sguardo.

> **Perché un giorno?** Perché una *forma* (un trend, un supporto, un breakout) è una cosa locale: succede in ore o giorni, non in 5 anni. 64 candele = un giorno intero di mercato (extended hours inclusi). La finestra si potrà **allargare** (2 giorni, una settimana) se servirà più contesto.

### Cosa porta ogni candela — la forma + i 45 sensi

Ogni candela non è solo 5 numeri (apertura, massimo, minimo, chiusura, volume). Porta con sé anche i suoi **45 indicatori** già calcolati — i suoi "sensi". Quindi una candela ≈ **50 numeri**. Vogliamo che, guardando un giorno, il sistema veda **la forma e tutti i sensi insieme**.

**Il problema: i numeri non sono confrontabili.** RSI sta tra 0 e 100, il MACD è piccolo (±2), l'OBV (volume cumulato) arriva ai milioni, il prezzo è ~$185, i pattern sono 100/0/-100. Se li diamo grezzi, i numeri grandi **schiacciano** i piccoli: l'OBV cancellerebbe l'RSI, e l'occhio vedrebbe solo il volume.

**La soluzione — tre mosse:**

1. **Normalizzare** — riportare ogni dato alla stessa scala (es. tra -1 e +1), così pesano tutti uguale e sono confrontabili. Una salita del 2% di NVDA e una di KO diventano identiche: conta la forma, non il titolo né il prezzo assoluto.
2. **Raggruppare per famiglia** — momentum, trend, volatilità, volume, Ichimoku.
3. **I pattern come bandierine** — segnali "acceso/spento" che si accendono nel giorno.

> Li mettiamo **tutti dentro, normalizzati**, e lasciamo che sia il risultato a dire quali contano. Se l'occhio fatica con troppi dati, si parte da un gruppo ridotto e si aggiungono. Il mercato decide, non noi.

### Come impara a vedere — prima ricopiare, poi la libreria

Procediamo a piccoli passi: gattona prima di camminare.

**Passo A — Imparare a ricopiare.** Prima una rete semplice (*autoencoder*) che fa una cosa sola: **guarda una finestra e prova a ridisegnarla**. Comprime il giorno in pochi numeri (la firma) e poi lo ricostruisce. Se ci riesce bene, ha capito la struttura. È facile da controllare e correggere.

**Passo B — Costruire la libreria.** Quando sa ricopiare, aggiungiamo un **dizionario di forme** (il *codebook*): invece di una firma libera, l'occhio sceglie la forma più simile da un archivio di forme tipiche. È il salto da autoencoder a **VQ-VAE** (Vector Quantized Variational Autoencoder). Quell'archivio **è** la libreria di grafici.

In sintesi, il meccanismo del VQ-VAE:

1. **Comprime** la finestra in una firma (riassume un giorno in pochi numeri).
2. **Sceglie un codice** dal dizionario interno — arrotonda la firma alla forma più simile.
3. **Ricostruisce** la finestra partendo solo dal codice scelto.
4. **Impara dall'errore**: dove ricostruisce male, aggiusta il dizionario. Nel tempo le forme diventano precise.

Il risultato è un **occhio** che trasforma qualsiasi giorno di grafico in una firma, e una **libreria** di forme leggibile e arricchibile. L'occhio resta invariato in tutti gli stadi successivi.

### La memoria dei pattern — la libreria visiva

Il codebook non è solo un componente interno: è la **memoria visiva** del sistema, una libreria di forme che cresce nel tempo.

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

Ogni pattern è un vettore di numeri, ma si può **visualizzare come grafico**. Puoi aprire la cartella, vedere cosa ha imparato il sistema, e **aggiungere pattern dai libri**. Non diventano regole rigide: se nei dati reali quel pattern ha anticipato movimenti, il sistema lo userà; se no, lo ignorerà. Il mercato resta il giudice.

La memoria cresce: pattern scoperti dallo storico (Stadio 1), pattern aggiunti dai libri, pattern rafforzati dalla ricompensa (Stadio 2), nuovi pattern dall'esperienza live.

### Come sappiamo che "ci vede" davvero — i 3 test

**Test 1 — Ricostruzione su dati mai visti.** Si tengono da parte alcuni mesi che il sistema non ha mai visto. Se riesce a ricopiarli bene, ha imparato strutture *generali*, non li ha memorizzati.

**Test 2 — Coerenza tra titoli diversi (il test chiave).** Si mettono le firme di migliaia di finestre su una mappa 2D (t-SNE o UMAP). Se la salita di NVDA finisce **vicino** alla salita di KO — titoli diversissimi, stessa forma — allora vede la *struttura*, non il titolo. Se invece i gruppi sono organizzati per titolo, l'occhio non funziona ancora.

**Test 3 — Stabilità nel tempo.** Una salita del 2021 e una del 2024 devono finire vicine sulla mappa: il mercato cambia, le forme di fondo restano.

Quando tutti e tre passano in modo stabile, lo Stadio 1 è completo e si passa allo Stadio 2.

---

## Stadio 2 — Associare

> Panoramica di cosa viene dopo. Il documento di dettaglio si scriverà quando lo Stadio 1 sarà completato e verificato — con i dati reali davanti, come prescrive la filosofia.

### L'obiettivo

Sopra l'occhio già addestrato si aggiunge una **testa decisionale**: una rete che prende la firma del pattern e risponde a *"Vista questa struttura, il prezzo salirà o scenderà nelle prossime candele?"*

È qui che entrano **la lista dei 45 indicatori e dei pattern** — per qualificare la situazione — e la **ricompensa**: se la previsione era giusta, segnale positivo; se sbagliata, negativo. Nel tempo il sistema impara quali situazioni sono state seguite da rialzi e quali da ribassi, senza che nessuno gliel'abbia detto.

### Perché la ricompensa si definisce solo qui

La definizione precisa della ricompensa — quanto movimento, in quante candele, con quale soglia — non si fissa adesso. Si definisce quando i dati reali sono davanti e si può osservare come il sistema risponde. Un bambino non nasce con le regole del bene e del male già scritte: le scopre vivendo. Definirla troppo presto rischia di ottimizzare la metrica sbagliata.

Quello che sappiamo già è la **soglia minima di successo**: accuracy direzionale **> 53% out-of-sample** — tre punti sopra il lancio di moneta, su dati mai visti.

### Cosa si mantiene dallo Stadio 1

L'occhio (l'encoder) rimane invariato. Non si ricomincia da zero: si aggiunge la testa decisionale sopra la stessa base. Per questo l'ordine è obbligatorio — non si può associare senza prima saper vedere.

---

## Stadio 3 — Contestualizzare (panoramica)

Dopo che il sistema sa vedere e associare su un singolo titolo, impara a guardare **i settori**: costruisce i grafici di settore, capisce **in giornata quale settore va meglio** e come i movimenti di un settore anticipano o trascinano gli altri (le rotazioni settoriali). Così sa **in che settore** cercare i pattern e investire. Qui rientra l'idea di dare al sistema, accanto al singolo titolo, un **riassunto di settore**. Si progetta dopo lo Stadio 2.

---

## La roadmap della Fase 2: i passi concreti

| # | Passo | Risultato atteso |
|---|---|---|
| 1 | **Preparare l'ambiente** — struttura cartelle `training/`, librerie (PyTorch, scikit-learn) | Ambiente pronto e verificato |
| 2 | **Preparare i dati** — finestre da un giorno, normalizzate, divise in train/validation/test (il test è un periodo *futuro*, mai a caso) | Finestre pronte, suddivisione documentata |
| 3 | **Occhio — Passo A** — addestrare l'autoencoder a ricopiare le finestre | L'occhio ricostruisce bene; perdita scesa e stabile |
| 4 | **Occhio — Passo B** — aggiungere il dizionario (codebook) → VQ-VAE | Nasce la libreria; modello salvato in `models/` |
| 5 | **Verifica** — i 3 test + visualizzare le forme scoperte | Mappa 2D coerente tra titoli, metriche documentate |
| 6 | **Arricchire** — aggiungere pattern dai libri alla libreria | `models/pattern_memory/` con pattern automatici + manuali |

Struttura delle cartelle e dettagli operativi nel [README di `training/`](../../training/README.md).

---

## Cosa cambia rispetto alla Fase 1

| Aspetto | Fase 1 | Fase 2 (Stadio 1) |
|---|---|---|
| Obiettivo | Costruire il mondo | Insegnare a vedere il mondo |
| Output | Database + dashboard | Occhio VQ-VAE + libreria pattern |
| Strumenti nuovi | DuckDB, pandas-ta, Plotly | PyTorch, autoencoder/VQ-VAE, t-SNE/UMAP |
| Come si valuta | Dati corretti? Dashboard funziona? | L'occhio vede strutture coerenti tra titoli diversi? |
| Ricompensa | Nessuna | Nessuna (arriva allo Stadio 2) |

---

## Il principio che non cambia

Un senso alla volta. Un passo alla volta. Si misura prima di aggiungere qualcosa. Si scala solo quando funziona.

Il bambino deve prima imparare a vedere bene, prima di poter capire cosa significano le cose che vede. Poi capire cosa significano, prima di imparare a sentire. La sequenza non è invertibile. La fretta produce sistemi che sembrano funzionare ma non funzionano.

---

*AI Market Predictor · Versione 4.0 · Fase 2 — Roadmap. Vedi anche [README di training/](../../training/README.md) e [documento principale](../Documento_Principale/README.md).*
