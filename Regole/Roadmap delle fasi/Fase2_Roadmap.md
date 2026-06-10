# AI MARKET PREDICTOR
### Fase 2 — Training: Stadio 1 (Vedere) e Stadio 2 (Associare)
*Un documento per capire cosa stiamo costruendo, perché, e come ci arriviamo.*

> **Stato: IN CORSO.** La Fase 1 — Fondamenta è completata. Questa è la roadmap della Fase 2.

---

## Prima di tutto: cosa cambia nella Fase 2

Nella Fase 1 abbiamo costruito il mondo. 3.508.587 candele, indicatori calcolati, database pulito, dashboard interattiva. Il bambino ha la scacchiera, i pezzi, e ha visto com'è fatta.

Nella Fase 2 il bambino comincia a giocare.

Ma non in modo caotico. Segue la stessa progressione naturale di un bambino che impara: prima impara a *vedere* (Stadio 1), poi impara a *collegare quello che vede a quello che succede dopo* (Stadio 2). Non si passa avanti finché il passo corrente non funziona in modo misurabile.

Tutto continua a girare in locale, sul Mac — esattamente come la Fase 1. Il server Hetzner entra solo quando il sistema dovrà girare H24 in autonomia, in fasi successive.

---

## Stadio 1 — Vedere

### L'obiettivo in una frase

Insegnare al sistema a riconoscere le **strutture** dei grafici — trend, supporti, pattern ricorrenti — senza ancora fare previsioni e senza ancora ricevere ricompensa. Prima di tutto, bisogna saper guardare.

### Il parallelo con il bambino

Un neonato all'inizio vede solo macchie sfocate. Col tempo la corteccia visiva si organizza: prima i bordi, poi le forme, poi gli oggetti. Il bambino riconosce una palla *prima* di sapere a cosa serve una palla. Il riconoscimento viene prima del significato.

Lo Stadio 1 costruisce la corteccia visiva del sistema per i grafici. Il sistema impara a distinguere "questa è una salita", "questo è un range laterale", "qui c'è una struttura di supporto" — senza ancora sapere se sia un bene o un male per il trading. Quello arriva allo Stadio 2.

### Cosa "vede" il sistema — lo stato

A ogni passo, il sistema non vede tutto il grafico dall'inizio. Vede una **finestra scorrevole** delle ultime N candele — esattamente come un trader che guarda lo schermo vede le ultime ore o i ultimi giorni, non tutta la storia del titolo.

Ogni candela della finestra porta con sé:
- **OHLC normalizzati** — non i prezzi assoluti (AAPL a $185 vs KO a $60), ma i rendimenti percentuali rispetto alla candela precedente. Una salita del 2% è uguale su qualsiasi titolo.
- **Volume normalizzato** — volume relativo rispetto alla media del periodo, non assoluto.
- **Indicatori già calcolati** — RSI, MACD, posizione nelle Bollinger Bands, EMA relativa, ATR. Sono già tutti nel database.

> **Perché normalizzare?** Per la stessa ragione per cui riconosciamo una "palla" sia da tennis sia da spiaggia. Una salita del 2% di NVDA e una salita del 2% di KO devono apparire identiche al sistema — conta la forma, non il titolo o il prezzo assoluto.

### Come impara senza ricompensa — il VQ-VAE

Questo è il punto tecnico centrale dello Stadio 1. Normalmente il Reinforcement Learning usa la ricompensa per imparare. Ma lo Stadio 1 non fa ancora previsioni — quindi non c'è ricompensa. Come impara?

Impara cercando di **comprendere la struttura di quello che vede**, usando i dati stessi come maestro. L'architettura scelta si chiama **VQ-VAE** (Vector Quantized Variational Autoencoder). Il nome è tecnico; il meccanismo è semplice:

**1. Comprime.** Il sistema riceve una finestra di candele e la "schiaccia" in un piccolo vettore di numeri — la firma matematica di quella struttura. Come riassumere un libro in una sola frase: si perde il dettaglio, ma si cattura l'essenza.

**2. Sceglie un codice.** Invece di usare la firma esatta, il sistema sceglie il codice più simile da un dizionario interno chiamato **codebook** — un insieme di forme fondamentali. È come arrotondare la propria frase a una delle frasi più comuni in un vocabolario limitato.

**3. Ricostruisce.** Partendo solo dal codice scelto, il sistema cerca di ricostruire la finestra originale. Se ci riesce bene, vuol dire che il codebook cattura le strutture essenziali del mercato.

**4. Impara dall'errore.** Dove la ricostruzione è imprecisa, il sistema aggiusta il codebook. Nel tempo, il codebook diventa sempre più preciso — e il sistema ha imparato a vedere le forme.

Il risultato finale è un **occhio** — un encoder capace di trasformare qualsiasi finestra di candele in una "firma" che ne descrive la struttura. Questo occhio è il pezzo fondamentale che rimane invariato in tutti gli stadi successivi.

### La memoria dei pattern — la libreria visiva

Il codebook non è solo un componente interno. È la **memoria visiva** del sistema — una libreria di forme che cresce nel tempo.

```
models/pattern_memory/
  codebook.npy           ← il dizionario interno (scoperto autonomamente)
  pattern_000.npy        ← forma 0: struttura laterale
  pattern_001.npy        ← forma 1: breakout rialzista
  pattern_002.npy        ← forma 2: trend ribassista prolungato
  ...
  book_testa_spalle.npy  ← aggiunto manualmente da libro di analisi
  book_doppio_massimo.npy
  ...
```

Ogni pattern è un vettore numerico, ma può essere visualizzato come grafico. Si può aprire la cartella, guardare cosa il sistema ha imparato a "vedere", e — cosa più importante — **aggiungere pattern manualmente**.

Se si prende un libro di analisi tecnica classica e si estraggono esempi di pattern noti — testa-spalle, doppio massimo, bandiera rialzista, triangolo simmetrico — questi possono essere aggiunti come voci aggiuntive nella memoria. Il sistema non li applica come regole rigide. Li tratta come qualsiasi altro pattern in memoria: se nei dati reali quel pattern ha portato a movimenti significativi, lo userà. Se non ha funzionato, lo ignorerà. Il mercato decide sempre.

Questa memoria **cresce con il tempo**:
- Stadio 1: pattern scoperti autonomamente dai 5 anni di storico
- Dopo Stadio 1: pattern aggiunti da libri e da conoscenza esterna
- Stadio 2: i pattern che si dimostrano predittivi vengono rafforzati dalla ricompensa
- Live: nuovi pattern scoperti dall'esperienza sul mercato reale vengono aggiunti

### Come sappiamo che "ci vede" davvero — le metriche dello Stadio 1

Il documento principale dice: *"Il sistema descrive correttamente la struttura del grafico che sta guardando, in modo stabile e coerente su più titoli diversi."* In pratica lo verifichiamo così:

**Test 1 — Ricostruzione su dati mai visti.**
Si separano prima del training alcuni mesi di dati (out-of-sample) — titoli e periodi che il sistema non ha mai visto durante l'addestramento. Se riesce a ricostruirli bene, ha imparato strutture generalizzabili, non ha memorizzato i dati specifici.

**Test 2 — Coerenza tra titoli diversi (il test chiave).**
Si prendono le firme (vettori) di migliaia di finestre di titoli diversi e le si proietta su una mappa 2D (con t-SNE o UMAP). Se la salita di NVDA finisce *vicino* alla salita di KO sulla mappa — due titoli completamente diversi, stessa forma — allora il sistema vede la struttura, non memorizza il titolo. Se invece i cluster sono organizzati per titolo invece che per forma, l'occhio non funziona ancora.

**Test 3 — Stabilità nel tempo.**
Le firme di strutture simili devono rimanere simili anche su periodi diversi. Una salita del 2021 e una salita del 2024 devono finire vicine sulla mappa — il mercato cambia, le strutture fondamentali rimangono.

Quando tutti e tre i test sono soddisfatti in modo stabile, lo Stadio 1 è completato e si passa allo Stadio 2.

---

## Stadio 2 — Associare

> Questa sezione è una panoramica di cosa viene dopo lo Stadio 1. Il documento di dettaglio dello Stadio 2 verrà scritto quando lo Stadio 1 sarà completato e verificato — con i dati reali davanti agli occhi, come prescrive la filosofia del progetto.

### L'obiettivo

Allo Stadio 2, sopra l'occhio già addestrato si aggiunge una **testa decisionale**: una rete che prende la firma del pattern e risponde alla domanda: *"Vista questa struttura, il prezzo salirà o scenderà nelle prossime N candele?"*

È qui che entra la **ricompensa** — la decisione più delicata di tutto il progetto. Se la previsione era giusta, il sistema riceve un segnale positivo. Se era sbagliata, uno negativo. Nel tempo impara quali pattern sono stati seguiti da rialzi e quali da ribassi, senza che nessuno gliel'abbia detto.

### Perché la ricompensa si definisce solo qui

La definizione precisa della ricompensa — quanto movimento, in quante candele, con quale soglia — non viene fissata adesso. Viene definita quando i dati reali sono davanti agli occhi e si può osservare come il sistema risponde.

Un bambino non nasce con le regole del bene e del male già scritte. Le scopre vivendo. Definire la ricompensa troppo presto, senza i dati, rischia di costruire un sistema che ottimizza la metrica sbagliata. Meglio aspettare.

Quello che sappiamo già è la **soglia minima di successo**: accuracy direzionale superiore al **53% out-of-sample** — tre punti percentuali sopra il lancio di moneta. Non basta funzionare sui dati di training. Deve funzionare su dati che non ha mai visto.

### Cosa si mantiene dallo Stadio 1

L'occhio VQ-VAE — l'encoder — rimane invariato. Non si ricomincia da zero: si aggiunge la testa decisionale sopra la stessa base. Le firme dei pattern che l'occhio ha già imparato a calcolare vengono usate direttamente come input per la testa.

Questo è il motivo per cui l'ordine è obbligatorio: non si può associare senza prima saper vedere. E non si può sentire (Stadio 4) senza aver già imparato ad associare e contestualizzare.

---

## La roadmap della Fase 2: i passi concreti

### Passo 1 — Preparare l'ambiente di training

Creare la struttura di cartelle per la Fase 2, installare le librerie necessarie (PyTorch, scikit-learn per la visualizzazione), e organizzare il codice in modo modulare. L'occhio, la memoria e la testa decisionale saranno componenti separati — così che uno possa essere aggiornato senza buttare via gli altri.

**Risultato atteso**: struttura `scripts/training/` pronta, librerie installate, ambiente verificato.

### Passo 2 — Preparare i dati per il training

Creare il dataset di training nel formato giusto per il VQ-VAE: finestre scorrevoli di N candele, normalizzate, suddivise in training / validation / test set. La separazione temporale è fondamentale: il test set deve essere un periodo futuro rispetto al training — non una selezione casuale.

**Risultato atteso**: file `.pt` (PyTorch tensor) con le finestre pronte, suddivisione train/val/test documentata.

### Passo 3 — Addestrare il VQ-VAE (l'occhio)

Addestrare il modello VQ-VAE sull'intero storico di training. Monitorare la perdita di ricostruzione durante il training. Il processo può richiedere ore sul Mac — è normale.

**Risultato atteso**: modello salvato in `models/`, curva di training documentata, perdita di ricostruzione scesa a un valore stabile.

### Passo 4 — Valutare l'occhio (Test 1, 2 e 3)

Eseguire i tre test descritti nella sezione "Come sappiamo che ci vede davvero":
- Ricostruzione su dati out-of-sample
- Mappa 2D delle firme per coerenza tra titoli
- Stabilità temporale dei pattern

Visualizzare i pattern nel codebook. Valutare cosa ha scoperto il sistema.

**Risultato atteso**: grafici dei pattern scoperti, mappa 2D che mostra coerenza tra titoli, metriche di ricostruzione documentate.

### Passo 5 — Arricchire la memoria con pattern da libri

Guardare i pattern scoperti automaticamente. Identificare quali pattern classici dell'analisi tecnica mancano o sono poco rappresentati. Aggiungere manualmente esempi da libri o risorse esterne.

**Risultato atteso**: cartella `models/pattern_memory/` con pattern automatici + pattern aggiunti manualmente, documentati e visualizzabili.

### Passo 6 — Dichiarare lo Stadio 1 completo e passare allo Stadio 2

Solo quando i tre test di verifica sono soddisfatti in modo stabile e la memoria è ricca e leggibile, lo Stadio 1 viene dichiarato completo. Si scrive un resoconto di cosa il sistema ha imparato, si aggiornano i documenti, e si inizia a progettare lo Stadio 2.

---

## Cosa cambia rispetto alla Fase 1

| Aspetto | Fase 1 | Fase 2 |
|---|---|---|
| Obiettivo | Costruire il mondo | Insegnare a vedere il mondo |
| Output | Database + dashboard | Occhio VQ-VAE + memoria pattern |
| Strumenti nuovi | DuckDB, pandas-ta, Plotly | PyTorch, VQ-VAE, t-SNE/UMAP |
| Durata stimata | Alcune settimane | Alcune settimane/mesi |
| Come si valuta | Dati corretti? Dashboard funziona? | L'occhio vede strutture coerenti tra titoli diversi? |
| Ricompensa | Nessuna | Nessuna (arriva allo Stadio 2) |

---

## Il principio che non cambia

Un senso alla volta. Un passo alla volta. Si misura prima di aggiungere qualcosa. Si scala solo quando funziona.

Il bambino deve prima imparare a vedere bene prima di poter capire cosa significano le cose che vede. Poi capire cosa significano prima di poter imparare a sentire. La sequenza non è invertibile. La fretta produce sistemi che sembrano funzionare ma non funzionano.

---

*AI Market Predictor · Versione 4.0 · Fase 2 — Roadmap*
