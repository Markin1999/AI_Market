# AI MARKET PREDICTOR
### Fase 1 — Dalle fondamenta alla prima immagine del mercato
*Un documento per capire cosa stiamo costruendo, perché, e come ci arriviamo.*

> **Stato: FASE 1 COMPLETATA.** Vedi la sezione "Dove siamo adesso" in fondo per il dettaglio di tutti i passi.

---

## Prima di tutto: cosa stiamo costruendo

Un sistema che impara a fare trading da solo — non perché gli insegniamo le regole, ma perché lo lasciamo fare esperienza.

L'idea di fondo è semplice. I sistemi di trading tradizionali vengono programmati: qualcuno scrive le regole, il computer le segue. Compra quando l'RSI scende sotto 30, vendi quando il MACD incrocia al ribasso. Queste regole funzionano finché il mercato si comporta come chi le ha scritte si aspettava. Poi il mercato cambia, e le regole smettono di funzionare.

Il nostro sistema funziona diversamente. Non gli programmiamo le regole. Gli creiamo l'ambiente giusto per impararle da solo, attraverso l'esperienza diretta con i dati reali del mercato. È lo stesso principio con cui un bambino impara cosa è caldo e cosa è freddo: non da una definizione, ma toccando le cose.

### Perché non basta comprare un ETF e aspettare?

È la domanda giusta, ed è quella che usiamo come benchmark finale. Se il sistema non riesce a fare meglio di un semplice investimento passivo sull'indice — comprare l'S&P500 e non toccare nulla — allora non vale la complessità, il tempo e il rischio che introduce. Il sistema deve guadagnarsi il diritto di esistere, ogni mese, contro il confronto più onesto che esiste.

### Un progetto in quattro stadi di crescita

Come un bambino che prima impara a vedere, poi a riconoscere, poi a contestualizzare, poi a sentire — il sistema segue la stessa progressione. I quattro stadi non sono arbitrari: ogni stadio costruisce sulle fondamenta del precedente, e non si passa avanti finché quello corrente non funziona in modo misurabile e stabile.

> **💡 Il principio chiave**
> Il sistema riceve dati. Fa una previsione. Il mercato gli risponde. Quella risposta — aveva ragione o torto? — è la sua unica guida. Nel tempo, attraverso milioni di questi cicli, costruisce da solo una mappa sempre più precisa di come funziona il mercato. Questo meccanismo si chiama Reinforcement Learning.

**1 · Stadio 1 — Vedere**
Il sistema impara a riconoscere le forme dei grafici. Un trend rialzista da uno ribassista. Supporti, resistenze, strutture di base. Prima di tutto, bisogna saper guardare.

**2 · Stadio 2 — Associare**
Il sistema inizia a collegare quello che vede ai movimenti successivi. Impara che certi pattern sono stati seguiti, più spesso, da rialzi. Inizia a fare previsioni e ricevere ricompensa.

**3 · Stadio 3 — Contestualizzare**
Lo stesso pattern in un settore forte si comporta diversamente che in un settore debole. Il sistema impara che i titoli non sono isole — fanno parte di famiglie che si muovono insieme.

**4 · Stadio 4 — Sentire**
Solo quando i primi tre stadi sono solidi, entrano le notizie. Le emozioni del mercato — paura, entusiasmo, incertezza — amplificano o smorzano i pattern tecnici. Il sistema le impara vivendo, non studiando archivi.

> **📋 Una nota sul metodo**
> Il sistema non vedrà mai soldi reali prima di almeno sei mesi di paper trading positivo — operazioni simulate su mercato reale, con tutte le metriche che devono essere superate. Non ci sono scorciatoie. La fretta produce sistemi che sembrano funzionare ma non funzionano.

---

## La Fase 1: costruire le fondamenta

Prima che il sistema possa imparare qualsiasi cosa, deve avere un mondo in cui farlo. La Fase 1 è la costruzione di quel mondo — e si fa interamente in locale, sul proprio computer.

Immagina di voler insegnare a qualcuno il gioco degli scacchi. Prima di spiegargli le mosse, prima di fargli fare una partita, devi avere una scacchiera. E i pezzi. E sapere dove metterli. La Fase 1 è costruire quella scacchiera — il database storico del mercato — in modo che il sistema abbia un terreno solido su cui iniziare a imparare.

Non è la parte glamour del progetto. Non ci sono algoritmi che imparano, non ci sono previsioni, non ci sono grafici che si muovono in tempo reale. È il lavoro di fondamenta: raccogliere dati reali di alta qualità, organizzarli in modo intelligente, e costruire gli strumenti per visualizzarli. Fatto bene, questo lavoro regge tutto quello che viene dopo. Fatto male, ogni cosa che ci costruiamo sopra sarà fragile.

Tutto questo — almeno nella Fase 1 — gira sul proprio Mac. Niente server remoti, niente infrastruttura complessa. Un account Polygon.io per i dati, Python con le librerie giuste, e un database locale. Il server remoto entrerà in gioco nelle fasi successive, quando il sistema dovrà girare in autonomia 24 ore su 24.

---

## Cosa facciamo concretamente

### 1. Scegliamo i titoli giusti

Il sistema non guarda il mercato intero. Lavora su un universo definito di 66 titoli, distribuiti su tutti gli 11 settori dell'S&P 500 — circa 6 per settore. La scelta non è casuale: ogni titolo è stato selezionato per alta liquidità, presenza continuativa negli ultimi anni, e capacità di rappresentare il suo settore in modo significativo.

Questa divisione settoriale non è solo un modo per organizzare i dati — è una scelta pedagogica. Il sistema imparerà che il mercato non è un insieme caotico di prezzi, ma un ecosistema con struttura. Quando il settore Technology si muove, spesso trascina o anticipa gli altri. Quando i difensivi salgono mentre i ciclici scendono, qualcosa nel ciclo economico sta cambiando. Queste dinamiche sono tra i pattern più ricorrenti e prevedibili del mercato.

| Settore | Titoli rappresentativi | Natura |
|---|---|---|
| Technology | AAPL, MSFT, NVDA, AMD, GOOGL, META | Guida il mercato |
| Financials | JPM, BAC, GS, MS, BRK.B, C | Ciclico, segue i tassi |
| Health Care | JNJ, UNH, PFE, ABBV, MRK, LLY | Difensivo |
| Consumer Discr. | AMZN, TSLA, HD, MCD, NKE, SBUX | Ciclico |
| Consumer Staples | PG, KO, PEP, WMT, COST, CL | Difensivo |
| Energy | XOM, CVX, COP, SLB, EOG, PSX | Correlato al petrolio |
| Industrials | CAT, BA, HON, UPS, GE, LMT | Ciclo economico |
| Materials | LIN, APD, NEM, FCX, ECL, VMC | Inflazione e domanda |
| Real Estate | AMT, PLD, CCI, EQIX, SPG, DLR | Segue i tassi |
| Utilities | NEE, DUK, SO, AEP, EXC, XEL | Difensivo, stabile |
| Communication Svc | NFLX, DIS, CMCSA, T, CHTR, VZ | Growth + media |

### 2. Raccogliamo la storia del mercato

Per ciascuno dei 66 titoli, raccogliamo anni di dati storici a candele da 15 minuti. Ogni candela è un'istantanea precisa: il prezzo di apertura, il massimo raggiunto, il minimo toccato, e il prezzo di chiusura in quei 15 minuti — più il volume, cioè quante azioni sono cambiate di mano.

I dati vengono scaricati da Polygon.io — uno dei fornitori più affidabili di dati finanziari storici. Il piano Starter dà accesso illimitato allo storico senza restrizioni sull'ampiezza temporale. Il download iniziale dell'intero storico richiede qualche ora — ma è un'operazione da fare una volta sola.

> **Perché 15 minuti?** I 5 minuti hanno troppo rumore — movimenti casuali che non significano nulla. I 30 minuti perdono dettaglio sui movimenti intraday importanti. I 15 minuti sono il punto di equilibrio: abbastanza reattivi da catturare i segnali reali, abbastanza filtrati da ridurre il rumore di fondo.

> **Perché anni di storia?** In più anni, il mercato attraversa cicli completi: rialzi prolungati, correzioni, crisi, recuperi. Il sistema deve imparare a riconoscere i pattern in tutte queste condizioni — non solo quando tutto va bene. Con anni di storia, ogni titolo accumula decine di migliaia di candele. Una base statistica solida.

### 3. Arricchiamo ogni candela con i sensi del sistema

Il sistema non vede solo i prezzi grezzi. Su ogni candela calcoliamo una serie di indicatori tecnici — strumenti matematici che trasformano la sequenza di prezzi in informazioni più facili da interpretare. Sono i sensi del sistema: modi per percepire aspetti del mercato che non sarebbero visibili guardando una singola candela.

- **RSI.** Misura la velocità e la forza del movimento. Quando sale troppo (sopra 70), il titolo potrebbe essere ipercomprato. Quando scende troppo (sotto 30), potrebbe essere ipervenduto. È un termometro della pressione sul prezzo.
- **MACD.** Confronta due medie mobili di velocità diverse. Quando si incrociano, spesso segnala un cambio di momentum — la forza di un trend che inizia a indebolirsi o a rafforzarsi.
- **EMA 20, 50, 200.** Medie mobili su orizzonti temporali diversi — breve, medio, lungo periodo. Quando il prezzo è sopra tutte e tre, il titolo è in tendenza rialzista su tutti gli orizzonti.
- **Bollinger Bands.** Tre linee che mostrano quanto il prezzo si sta espandendo o contraendo rispetto al suo comportamento normale. Quando il prezzo tocca la banda superiore o inferiore, qualcosa di inusuale sta succedendo.
- **ATR.** Misura quanto si muove tipicamente quel titolo. Un ATR alto significa alta volatilità. Serve per capire quanto è normale aspettarsi di guadagnare o perdere su quel titolo in un certo periodo.
- **Pattern di candele.** Oltre 60 formazioni visive riconoscibili nelle candele giapponesi — hammer, engulfing, doji, e via dicendo. Ogni pattern è codificato come segnale di possibile inversione o continuazione del trend.

### 4. Organizziamo tutto in un database intelligente

Tutti questi dati vengono salvati in DuckDB, un database progettato specificamente per questo tipo di lavoro: query veloci su enormi quantità di dati storici. Non è un foglio Excel. È un motore analitico che può rispondere in pochi secondi a domande come: dammi tutte le candele di AAPL degli ultimi 90 giorni dove l'RSI era sotto 30 e il volume era doppio rispetto alla media.

Il database diventa la memoria permanente del sistema. Ogni candela scaricata rimane lì, organizzata per ticker e per data, pronta per essere usata in qualsiasi momento — sia per addestrare il modello nelle fasi successive, sia per generare grafici, sia per calcolare metriche di performance.

> **💾 Quanto spazio occupa tutto?** Con anni di candele 15 minuti per 66 titoli, con tutti gli indicatori calcolati, il database pesa intorno ai 200-300 megabyte. Una dimensione gestibilissima su qualsiasi Mac moderno. DuckDB lo legge in memoria in pochi secondi.

### 5. Visualizziamo quello che abbiamo costruito

L'obiettivo finale della Fase 1 è semplice: aprire il Mac, lanciare uno script, e vedere i grafici del mercato sullo schermo. Non un'immagine statica — grafici interattivi, zoomabili, navigabili. Candlestick con indicatori sovrapposti, heatmap dei settori, pannelli RSI e volume.

Prima di passare all'addestramento del sistema, dobbiamo poter vedere quello che abbiamo costruito. Non per abitudine — ma perché è l'unico modo per verificare che i dati siano puliti, che gli indicatori siano calcolati correttamente, e che il sistema abbia effettivamente un mondo coerente in cui vivere. Un grafico ti dice immediatamente se qualcosa non va. Prima di fidarci dei dati per addestrare un sistema di apprendimento, dobbiamo averli guardati con i nostri occhi.

- **Grafico candlestick per ogni titolo.** La vista fondamentale: prezzi a 15 minuti, con medie mobili e Bollinger Bands sovrapposte. Si può selezionare qualsiasi titolo e qualsiasi periodo.
- **Pannello RSI e MACD.** Gli indicatori di momentum visualizzati sotto il grafico principale, sincronizzati sulla stessa scala temporale.
- **Heatmap settoriale.** Tutti i 66 titoli mostrati per settore, colorati in base alla performance. Verde quando salgono, rosso quando scendono. Un colpo d'occhio sul mercato intero.
- **Stato del database.** Una schermata che mostra per ogni ticker quante candele sono state scaricate, da quando a quando, e se ci sono buchi o errori.

---

## Cosa ci serve per iniziare

Tutta la Fase 1 gira sul proprio Mac. Non serve nessun server remoto, nessuna infrastruttura complessa. Solo tre cose.

**Python — già installato.** Python è il linguaggio con cui costruiamo tutto il sistema. È lo standard de facto per il machine learning e l'analisi dati — tutte le librerie di cui abbiamo bisogno esistono già, sono mature, e sono gratuite. Non bisogna installarlo: è già presente sul Mac. Quello che installiamo sono le librerie specifiche: DuckDB per il database, pandas per la manipolazione dei dati, pandas-ta per il calcolo automatico degli indicatori tecnici, e Plotly per i grafici interattivi. Tutte gratuite, tutte open source, tutte con un comando di installazione.

**Polygon.io — il fornitore di dati.** Polygon.io è la fonte da cui il sistema scarica tutti i dati storici di mercato. Fornisce candele OHLCV a qualsiasi timeframe, su tutti i titoli quotati nelle borse americane, con uno storico che copre anni di storia. Il piano Starter, a circa 29 dollari al mese, dà accesso illimitato senza restrizioni temporali. Una volta creato l'account, Polygon fornisce una API key — una stringa di testo che il sistema usa per autenticarsi e scaricare i dati. È l'unica credenziale di cui abbiamo bisogno per tutta la Fase 1.

> **Costo Polygon.io Starter** — Circa 29 dollari al mese (~27 euro). È l'unico costo della Fase 1. Tutto il resto — Python, DuckDB, pandas, Plotly — è gratuito e open source.

> **Perché non i dati gratuiti?** I piani gratuiti di qualsiasi fornitore limitano la storia a 1-2 anni e spesso non includono i dati intraday a 15 minuti. Per costruire un sistema che impara dai cicli di mercato, servono almeno 5-6 anni di storia completa.

> **📌 Nessun server remoto nella Fase 1** — Hetzner e qualsiasi altra infrastruttura cloud entrano in gioco solo nelle fasi successive, quando il sistema dovrà girare in autonomia H24. Per ora, tutto gira sul Mac. Il costo mensile della Fase 1 è solo quello di Polygon.io.

---

## La roadmap: i passi della Fase 1

La Fase 1 si sviluppa in cinque passi sequenziali. Ognuno costruisce sul precedente. Non si passa avanti finché il passo corrente non funziona e non è stato verificato con i propri occhi.

### Passo 1 — Preparare l'ambiente di lavoro  ·  ✅ COMPLETATO
Si crea la struttura delle cartelle del progetto sul Mac, si installa l'ambiente Python con tutte le librerie necessarie, e si configura la connessione a Polygon.io con la API key. Alla fine di questo passo, tutto è pronto per ricevere i dati — ma il database è ancora vuoto.

### Passo 2 — Scaricare lo storico completo  ·  ✅ COMPLETATO
Si avvia il download dello storico: anni di candele 15 minuti per tutti i 66 titoli. Il sistema scarica i dati da Polygon.io, li valida, calcola gli indicatori tecnici per ogni candela, e li salva nel database DuckDB. L'operazione richiede alcune ore e viene fatta una volta sola. Alla fine, il database contiene milioni di candele pronte per essere usate.
**Risultato: 3.508.587 candele scaricate.**

### Passo 3 — Verificare la qualità dei dati  ·  ✅ COMPLETATO
Prima di fidarci dei dati, li guardiamo. Si aprono i grafici, si confrontano periodi storici noti con quello che il sistema ha scaricato, si verifica che gli indicatori tecnici siano calcolati correttamente. Questa fase di verifica è non negoziabile: dati sporchi o incompleti producono un sistema che impara le cose sbagliate.
**Risultato: controlli base e approfonditi superati, 0 problemi critici. Scoperto e corretto il problema del ticker META (vedi sotto).**

### Passo 4 — Costruire la dashboard di visualizzazione  ·  ✅ COMPLETATO
Si completano i grafici interattivi: candlestick per ogni titolo con indicatori sovrapposti, heatmap settoriale, stato del database. L'obiettivo concreto è aprire il Mac, lanciare uno script, e vedere i grafici del mercato sullo schermo — navigabili, zoomabili, selezionabili per titolo e periodo.
**Risultato: dashboard con 4 tab e timeframe adattivo, fluida anche su 5 anni di dati.**

### Passo 5 — Validare e dichiarare la Fase 1 completa  ·  ✅ COMPLETATO
Si esegue una verifica finale su tutto: il database è completo? Gli indicatori sono corretti? I grafici sono visibili e leggibili? Solo quando tutte le risposte sono sì, la Fase 1 è dichiarata completa e si può iniziare a pensare allo Stadio 1 — il primo addestramento del sistema.
**Risultato: tutte le risposte sono sì. Fase 1 dichiarata completa.**

> **📅 Tempistica realistica** — La Fase 1 completa richiede alcune settimane di lavoro, con sessioni regolari. Il download dello storico si avvia e si lascia girare da solo. Il resto è configurazione, verifica e raffinamento progressivo.

---

## Come si usa questo documento

Questo documento è la memoria del progetto. Claude AI non ricorda le conversazioni precedenti — ogni nuova sessione riparte da zero.

Per continuare il lavoro in qualsiasi momento, basta aprire una nuova chat con Claude, allegare questo documento, e scrivere: *"Questo è il documento del progetto AI Market Predictor. Siamo arrivati fino a [punto X]. Oggi vogliamo lavorare su [obiettivo]."* Claude rilegge il documento e riparte esattamente da dove ci si era fermati.

Il documento va aggiornato alla fine di ogni sessione di lavoro significativa — ogni volta che si completa un passo, si prende una decisione tecnica importante, o si scopre qualcosa di rilevante. In questo modo, la memoria del progetto cresce insieme al sistema, e non si perde nulla.

---

## Dove siamo adesso — FASE 1 COMPLETATA ✅

> Aggiornato al termine della Fase 1.

La Fase 1 è **completa in tutti e cinque i passi**. Il mondo in cui il sistema nascerà esiste, è stato verificato con i propri occhi, ed è pulito.

**Riepilogo di quanto realizzato:**

| Passo | Stato | Risultato |
|---|---|---|
| 1 — Ambiente | ✅ | venv Python, librerie, API key Polygon.io e FRED configurate |
| 2 — Download storico | ✅ | 3.508.587 candele 15min, 66 ticker, giugno 2021 → giugno 2026 |
| 3 — Verifica qualità | ✅ | Controlli base + approfonditi (8 categorie), 0 problemi critici |
| 4 — Dashboard | ✅ | 4 tab interattive, timeframe adattivo, fluida su 5 anni |
| 5 — Validazione | ✅ | Database completo, pulito, visualizzato — Fase 1 dichiarata completa |

**Cosa c'è in più rispetto al piano originale** (preparazione anticipata alla Fase 2):
- Dati macroeconomici scaricati da FRED (VIX, Fed rate, CPI, disoccupazione) — 1.826 giorni.
- Dataset di training assemblato (`dataset.parquet`): candele + macro + target del rendimento successivo.

**Scoperta durante la verifica** — proprio guardando il grafico "Settori nel tempo", come prescrive il metodo: il ticker **META** conteneva i dati di un'altra azienda prima del 9 giugno 2022 (Facebook ha tradato come "FB" fino a quella data, poi ha cambiato ticker in META). I dati sporchi sono stati rimossi e gli indicatori ricalcolati. È l'unico dei 66 titoli con questo problema. *Un grafico ti dice immediatamente se qualcosa non va* — ed è successo davvero.

**Prossimo passo: Fase 2 — Training.** Costruzione dell'ambiente di Reinforcement Learning e avvio dello Stadio 1 (Vedere). Qui verrà definita la ricompensa, con i primi dati reali davanti agli occhi.

---

*AI Market Predictor · Versione 4.0 · Fase 1 — Roadmap aggiornata*
