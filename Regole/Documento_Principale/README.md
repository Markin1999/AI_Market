# AI MARKET PREDICTOR
### Versione 4.0 — Architettura e memoria del progetto
**Un trader artificiale che impara come un bambino**

---

## Scheda riassuntiva del progetto

| Parametro | Valore |
|---|---|
| Obiettivo | Trader artificiale che impara da solo attraverso rinforzo — non viene programmato, viene fatto crescere |
| Universo titoli | 60-80 titoli — 5-7 per ciascuno degli 11 settori S&P500 |
| Frequenza candele | 15 minuti |
| Anni di storia | 5-7 anni (almeno 2 cicli completi di mercato) |
| Meccanismo di apprendimento | Reinforcement Learning — il mercato è il maestro, la ricompensa è l'unica guida |
| Stadi di apprendimento | 4 stadi in sequenza: Vedere → Associare → Contestualizzare → Sentire |
| Notizie | Introdotte in tempo reale solo dallo Stadio 4 — vissute, non studiate dallo storico |
| Claude API | Sistema emotivo sulle notizie (da -1 a +1) + analisi errori settimanale |
| Ricompensa | Da definire nella fase di costruzione con i primi dati reali davanti |
| Conoscenza del dominio | Fornita da Claude AI — il sistema non parte da zero sul trading |
| Costo mensile a regime | ~45-55 euro/mese |
| Prima esposizione reale | Solo dopo 6 mesi di paper trading positivi con tutte e 4 le metriche superate |

---

## 1. Filosofia — Il bambino che impara

Questo sistema non viene programmato per fare trading. Viene fatto crescere.

Un bambino non nasce sapendo cosa è pericoloso e cosa è sicuro. Osserva il mondo, tocca le cose, riceve segnali — si brucia, sorride, cade, ride. Nel tempo costruisce una mappa sempre più precisa di come funziona la realtà. Non gli viene spiegato tutto in anticipo — impara vivendo.

Il sistema funziona allo stesso modo. Nasce con i dati grezzi del mercato — prezzi, volumi, candele. Non sa ancora cosa significa un pattern rialzista o ribassista. Lo scopre lui, attraverso il ciclo continuo di osservazione, azione e ricompensa.

La conoscenza del trading — i principi, le regole, la logica dei mercati — viene fornita da Claude AI e costruita insieme nel tempo. Il sistema non parte da zero su questo: ha già accesso a una base di conoscenza che cresce ad ogni sessione di lavoro. Ciò che invece deve scoprire da solo è come quella conoscenza si applica ai dati reali, in tempo reale, con la ricompensa del mercato come unico giudice.

### Il ciclo fondamentale

| Fase | Cosa succede nel sistema | Parallelo con il bambino |
|---|---|---|
| Osserva | Riceve i dati di mercato — candele, volumi, indicatori, movimenti settoriali | Il bambino vede il mondo intorno a sé |
| Riconosce | Identifica una forma, una struttura, un pattern nei dati | Il bambino riconosce una forma o una situazione familiare |
| Agisce | Fa una previsione — questo titolo salirà o scenderà | Il bambino tocca, prova, sperimenta |
| Riceve ricompensa | Il mercato risponde — aveva ragione o torto? La ricompensa rinforza o corregge | Il bambino si brucia oppure sorride |
| Impara | Aggiorna il suo comportamento per il ciclo successivo — è leggermente più bravo | Il bambino non tocca più il fuoco — o ripete ciò che funzionava |

Questo meccanismo si chiama Reinforcement Learning. Non gli diciamo cosa cercare — lo lasciamo scoprire. Il mercato è il maestro. La ricompensa è l'unica guida.

---

## 2. Il mondo in cui il sistema nasce — I dati

Il sistema nasce dentro un mondo preciso. Quel mondo è costruito con dati reali di mercato, organizzati in modo che il sistema possa imparare a leggerli progressivamente, un livello alla volta.

### 2.1 I titoli — divisi per settore

Il sistema non analizza tutti i titoli allo stesso modo. Li vede come famiglie — gruppi di aziende che si muovono in modo correlato, che reagiscono agli stessi eventi, che rappresentano pezzi diversi dell'economia reale.

Questa divisione settoriale è fondamentale: insegna al sistema che il mercato non è un insieme caotico di prezzi, ma un ecosistema con struttura. Quando un settore si muove, spesso trascina o anticipa altri settori. Le rotazioni settoriali — denaro che esce dal tech ed entra nelle utilities, o viceversa — sono tra i movimenti più prevedibili e ricorrenti del mercato. Il sistema le imparerà nello Stadio 3.

| Settore | Titoli rappresentativi | Caratteristica chiave |
|---|---|---|
| Technology | AAPL, MSFT, NVDA, AMD, GOOGL | Guida spesso i movimenti dell'intero mercato |
| Financials | JPM, BAC, GS, MS, BRK.B | Sensibile ai tassi di interesse e al ciclo del credito |
| Health Care | JNJ, UNH, PFE, ABBV, MRK | Difensivo — regge nei mercati in ribasso |
| Consumer Discretionary | AMZN, TSLA, HD, MCD, NKE | Ciclico — riflette la fiducia dei consumatori |
| Consumer Staples | PG, KO, PEP, WMT, COST | Difensivo — prodotti di prima necessità |
| Energy | XOM, CVX, COP, SLB, EOG | Correlato al prezzo del petrolio e alla geopolitica |
| Industrials | CAT, BA, HON, UPS, GE | Indicatore del ciclo economico globale |
| Materials | LIN, APD, NEM, FCX, ECL | Sensibile all'inflazione e alla domanda globale |
| Real Estate | AMT, PLD, CCI, EQIX, SPG | Sensibile ai tassi — si comporta come le obbligazioni |
| Utilities | NEE, DUK, SO, AEP, EXC | Difensivo — domanda stabile indipendente dal ciclo |
| Communication Services | META, NFLX, DIS, CMCSA, T | Mix tra growth tecnologico e media tradizionale |

### 2.2 Le candele a 15 minuti — la lingua del sistema

Ogni candela a 15 minuti è una parola nel linguaggio che il sistema sta imparando. Contiene quattro informazioni: il prezzo di apertura, il massimo, il minimo, e il prezzo di chiusura. Più il volume — quante azioni sono cambiate di mano in quel periodo.

La scelta di 15 minuti è deliberata. I 5 minuti hanno troppo rumore — movimenti casuali che non significano nulla. I 30 minuti perdono dettaglio sui movimenti intraday importanti. I 15 minuti sono il punto di equilibrio: abbastanza reattivi da catturare i segnali reali, abbastanza filtrati da ridurre il rumore.

Con 5-7 anni di storia a 15 minuti, ogni titolo accumula circa 100.000-140.000 candele. È la base statistica necessaria perché il sistema possa distinguere i pattern ricorrenti dal caso puro.

### 2.3 Gli indicatori tecnici — i sensi del bambino

Il sistema non vede solo i prezzi grezzi. Ha sensi aggiuntivi che gli permettono di percepire aspetti del mercato non visibili a occhio nudo su una singola candela.

| Indicatore | Cosa misura | Cosa insegna al sistema |
|---|---|---|
| RSI | Velocità e forza del movimento dei prezzi — scala da 0 a 100 | Quando un titolo è in ipercomprato (>70) o ipervenduto (<30) |
| MACD | Differenza tra due medie mobili — segnala cambi di momentum | Quando la forza di un trend sta cambiando direzione |
| EMA 20/50/200 | Medie mobili esponenziali su diversi orizzonti temporali | La tendenza di breve, medio e lungo periodo del titolo |
| Bollinger Bands | Volatilità del titolo rispetto alla sua media storica | Quando il prezzo si espande o contrae rispetto al suo comportamento normale |
| ATR | Average True Range — ampiezza media dei movimenti in un periodo | Quanto si muove tipicamente quel titolo — utile per calibrare la ricompensa |
| Volume | Quante azioni sono cambiate di mano in quella candela | Se un movimento è supportato da partecipazione reale o è debole e inaffidabile |
| Pattern candele | 60+ formazioni visive riconoscibili nelle candele giapponesi | Segnali di inversione o continuazione codificati dalla tradizione tecnica |

---

## 3. Come il sistema impara — Reinforcement Learning

### 3.1 Il meccanismo di ricompensa

Il cuore del sistema è la ricompensa. Ogni volta che il sistema fa una previsione, il mercato gli risponde. Quella risposta è la ricompensa — positiva se aveva ragione, negativa se aveva torto. Nel tempo il sistema impara a fare previsioni sempre più accurate per massimizzare la ricompensa cumulativa.

La definizione precisa della ricompensa — quanto movimento, in quante candele, con quale soglia — è la decisione più delicata di tutto il progetto. Non viene definita adesso. Viene definita nella fase di costruzione, quando i primi dati reali sono davanti agli occhi e si può osservare come si comporta il sistema con diverse configurazioni.

Nota importante: definire la ricompensa troppo presto, senza dati reali, rischia di costruire un sistema che ottimizza la metrica sbagliata. Un bambino non nasce con le regole del bene e del male già scritte — le scopre vivendo. Faremo lo stesso.

### 3.2 I 4 stadi di apprendimento — dal semplice al complesso

Il sistema non impara tutto insieme. Come un bambino, sviluppa le competenze in ordine di complessità crescente. Ogni stadio costruisce sulla base del precedente. Non si passa allo stadio successivo senza che quello corrente sia stabile e misurabile.

| Stadio | Nome | Cosa impara | Come si misura | Condizione per avanzare |
|---|---|---|---|---|
| 1 | Vedere | Riconosce le forme dei grafici. Distingue un trend rialzista da uno ribassista. Identifica supporti, resistenze, e le strutture di base del movimento dei prezzi. | Il sistema descrive correttamente la struttura del grafico che sta guardando, in modo stabile e coerente su più titoli diversi. | Coerenza stabile su più titoli e periodi |
| 2 | Associare | Collega i pattern ai movimenti successivi. Impara che certi setup sono stati seguiti più spesso da rialzi, altri da ribassi. Inizia a fare previsioni e ricevere ricompensa. | Accuracy direzionale superiore al 50% su dati non visti prima durante l'addestramento. | Accuracy stabile sopra il 53% out-of-sample |
| 3 | Contestualizzare | Impara che lo stesso pattern in un settore forte si comporta diversamente rispetto a un settore debole. Scopre le rotazioni settoriali — denaro che esce dal tech ed entra nelle utilities. Vede i titoli come membri di famiglie, non come entità isolate. | Performance migliorata rispetto allo Stadio 2 quando usa il contesto settoriale. Se togliendo l'informazione settoriale le performance peggiorano, il sistema la sta usando davvero. | Miglioramento misurabile su paper trading con contesto vs senza |
| 4 | Sentire | Inizia a ricevere le notizie in tempo reale. Impara lentamente la correlazione tra il sentiment delle notizie e i movimenti successivi dei prezzi. Questo senso si sviluppa solo dopo che i primi tre stadi sono solidi — esattamente come le emozioni per un bambino. | Le previsioni migliorano in modo misurabile quando include il sentiment delle notizie rispetto a quando non lo include. | Miglioramento misurabile con notizie vs senza notizie |

### 3.3 Perché questa sequenza è obbligatoria

La sequenza degli stadi non è arbitraria. Ogni stadio presuppone il precedente:

- Non puoi contestualizzare (Stadio 3) se non sai ancora associare pattern a movimenti (Stadio 2).
- Non puoi associare (Stadio 2) se non sai ancora vedere le strutture di base (Stadio 1).
- Non puoi integrare le notizie (Stadio 4) se non hai già una base tecnica solida — le notizie amplificano o smorzano i pattern, ma non possono sostituirli.

Un bambino impara prima cosa è il caldo, poi impara che il caldo in estate è normale e il caldo in inverno è strano. La sequenza non è invertibile.

---

## 4. Le notizie — il sistema emotivo

Le notizie sono le emozioni del mercato. Esattamente come le emozioni per un bambino — non cambiano le leggi fisiche del mondo, ma amplificano o smorzano le reazioni a quello che sta succedendo.

Un bambino impara prima le leggi fisiche del mondo — la gravità, il caldo, il freddo. Solo dopo inizia a capire le emozioni — la paura, l'entusiasmo, la tristezza — e come queste modificano il comportamento suo e degli altri. Il sistema segue lo stesso ordine.

| Fase | Relazione con le notizie |
|---|---|
| Stadi 1-3 | Il sistema non vede le notizie. Impara solo dai dati tecnici. Questo è deliberato — serve costruire una base solida prima di aggiungere la complessità del linguaggio e del contesto delle news. |
| Ingresso notizie (Stadio 4) | Quando lo Stadio 3 è stabile, il sistema inizia a ricevere le notizie in tempo reale — solo da quel momento in poi. Non vengono usati archivi storici di notizie. Il sistema le vive, non le studia a ritroso. Questo è fondamentale: le notizie devono essere un'esperienza vissuta, non un'informazione retrospettiva. |
| Apprendimento emotivo | Il sistema osserva cosa succede ai prezzi dopo ogni notizia che riceve. Nel tempo costruisce da solo la correlazione — questo tipo di notizia tende ad amplificare i movimenti rialzisti, quest'altro li smorza. Non glielo insegniamo noi — lo scopre attraverso la ricompensa. |
| Ruolo di Claude | Claude legge ogni notizia e la traduce in un valore numerico di sentiment da -1 (molto negativo) a +1 (molto positivo). Questo valore entra come input aggiuntivo nel sistema accanto ai dati tecnici. Claude porta la conoscenza del linguaggio e del contesto — il sistema porta l'esperienza accumulata di cosa è successo dopo. |

---

## 5. Claude API — due ruoli distinti

Claude API non è uno strumento di reporting. Ha due ruoli precisi nel sistema, attivi in momenti e con obiettivi diversi.

| Ruolo | Quando | Input | Output |
|---|---|---|---|
| Sistema emotivo sulle notizie | In tempo reale, dallo Stadio 4 in poi | Notizie delle ultime ore per il titolo o il settore che il sistema sta analizzando in quel momento | Valore sentiment da -1 a +1 che entra come input aggiuntivo nel modello accanto ai dati tecnici |
| Analisi errori settimanale | Una volta a settimana, da subito — da tutti gli stadi | Log degli ultimi 7 giorni: segnali emessi, risultati reali, pattern di errore sistematici | Dove il sistema sbaglia sistematicamente? In quali condizioni di mercato i segnali sono inaffidabili? Suggerimenti per il ciclo successivo |

Questa struttura mantiene il costo API basso e il valore alto. Claude interviene solo dove la comprensione del linguaggio e del contesto cambia davvero la qualità dell'informazione — non per generare testo descrittivo che il sistema potrebbe produrre da solo con calcoli numerici.

---

## 6. Validazione — come sappiamo se funziona

Il sistema non viene mai considerato pronto per soldi reali basandosi su sensazioni o su risultati sui dati storici. Esistono quattro metriche precise che devono essere superate tutte e quattro su dati out-of-sample. Non ci sono eccezioni.

| Metrica | Soglia minima | Perché questa soglia |
|---|---|---|
| Accuracy direzionale | > 53% out-of-sample | Il 50% è un lancio di moneta. Servono almeno 3 punti percentuali di edge reale per coprire i costi operativi e giustificare il rischio aggiuntivo rispetto al non fare nulla. |
| Sharpe ratio | > 1.0 su 6 mesi | Misura la qualità del rendimento, non solo la quantità. Un sistema che guadagna il 10% con volatilità altissima è peggiore di uno che guadagna il 6% con stabilità. Sopra 1.0 è accettabile, sopra 2.0 è ottimo. |
| Drawdown massimo | < 20% | Sopra il 20% di perdita dal picco, diventa psicologicamente impossibile continuare a seguire il sistema. La disciplina crolla prima dei soldi. Il sistema deve essere sostenibile anche emotivamente. |
| Confronto vs Buy&Hold | Superiore su 2+ anni | Se il sistema non batte la strategia passiva di comprare l'indice e aspettare, non vale la complessità, il tempo e il rischio aggiuntivo che introduce. È il benchmark minimo di utilità. |

---

## 7. Paper trading — 6 mesi obbligatori

Il paper trading non è una formalità. È l'unico modo per sapere se il sistema funziona nel mondo reale, fuori dai dati storici su cui ha imparato. Un modello che funziona benissimo sui dati passati quasi sempre smette di funzionare quando il mercato cambia regime.

Durata minima: 6 mesi. Non si abbrevia per nessun motivo, nemmeno se i risultati sembrano ottimi nelle prime settimane. Servono diversi regimi di mercato — rialzo, laterale, ribasso, alta volatilità — per avere evidenza statistica reale e non illudersi con un momento favorevole.

| Periodo | Obiettivo | Criterio per avanzare |
|---|---|---|
| Mesi 1-2 | Setup del simulatore. Prime operazioni virtuali. Verifica che i segnali siano coerenti con la logica attesa. Identificazione dei primi bug e anomalie. | Pipeline stabile. Nessun errore critico. Dati puliti e continui per almeno 4 settimane consecutive. |
| Mesi 3-4 | Raccolta sistematica delle metriche. Identificazione dei pattern di errore con analisi Claude settimanale. Prime ottimizzazioni basate su evidenza reale, non su intuizioni. | Accuracy superiore al 53%. Comportamento stabile in diversi contesti di mercato — non solo in mercati favorevoli. |
| Mesi 5-6 | Analisi completa: Sharpe, drawdown, confronto Buy&Hold. Revisione approfondita dei log errori con Claude. Decisione informata e basata su dati reali sul passo successivo. | Tutte e quattro le metriche superate. Solo allora si valuta la prima esposizione reale. |

Alla fine dei 6 mesi esistono tre scenari. Risultati ottimi: prima esposizione reale con 200-500 euro massimo e stop loss obbligatori su ogni posizione. Risultati misti: altri 3 mesi di ottimizzazione mirata. Risultati negativi: si torna allo stadio di apprendimento precedente e si identifica il problema prima di riprendere.

---

## 8. Stack tecnologico

| Componente | Tecnologia | Costo | Ruolo nel sistema |
|---|---|---|---|
| Server H24 | Hetzner CX32 | 8 euro/mese | Esegue tutto in autonomia senza Mac acceso — il sistema lavora anche di notte |
| Dati mercato | Polygon.io Starter | ~27 euro/mese | Candele 15min live e storiche su tutti i titoli + notizie per titolo e settore |
| Database | DuckDB | Gratuito | Gestisce milioni di righe di candele storiche con query analitiche veloci |
| Indicatori tecnici | pandas-ta | Gratuito | RSI, MACD, EMA, Bollinger Bands, ATR, Volume, 60+ pattern candele giapponesi |
| Dati macro | FRED API | Gratuito | Fed, CPI, NFP, earnings calendar — il contesto macro per ogni periodo storico e live |
| Cervello AI | Claude API (Anthropic) | ~10 euro/mese | Sentiment notizie da -1 a +1 in tempo reale + analisi errori settimanale sui log |
| Modello RL | PyTorch + algoritmo RL | Gratuito | Il cervello che impara attraverso i 4 stadi — si costruisce e si raffina progressivamente |
| Dashboard | Plotly / Python | Gratuito | Grafici live, heatmap settoriale, metriche paper trading, log errori visualizzati |
| Linguaggio | Python | Gratuito | Standard de facto per ML e analisi dati — tutte le librerie necessarie sono disponibili |

---

## 9. Costi mensili

Soldi esposti al mercato: zero fino alla fine del paper trading. Prima esposizione reale: 200-500 euro massimo, con stop loss obbligatori su ogni posizione. Il sistema suggerisce — l'utente approva ogni operazione manualmente per almeno i primi 12 mesi.

| Voce | Stadi 1-3 | Stadio 4 + paper trading | Sistema completo |
|---|---|---|---|
| Hetzner server | 8 euro | 8 euro | 18 euro (upgrade CX42) |
| Polygon.io | ~27 euro | ~27 euro | ~27 euro |
| Claude API | ~5 euro | ~10 euro | ~10 euro |
| Tutto il resto | 0 euro | 0 euro | 0 euro |
| **Totale mensile** | **~40 euro** | **~45 euro** | **~55 euro** |

---

## 10. Principi operativi — le regole che non cambiano

| Principio | Regola concreta |
|---|---|
| Il sistema impara, non viene programmato | Non si codificano regole di trading nel modello. Si crea l'ambiente di apprendimento e si lascia che il sistema scopra i pattern da solo attraverso il ciclo osserva-agisce-ricompensa. |
| Un stadio alla volta | Non si passa allo stadio successivo senza che quello corrente abbia dimostrato di funzionare con metriche misurabili. La fretta produce sistemi che sembrano funzionare ma non funzionano. |
| Un senso alla volta | Le notizie entrano solo dopo che i pattern tecnici degli Stadi 1-3 sono appresi in modo stabile. Aggiungere complessità prima che la base sia solida produce confusione, non miglioramento. |
| La ricompensa si definisce con i dati | Il meccanismo di ricompensa viene definito quando i primi dati reali sono disponibili — non in anticipo. Un bambino non nasce con le regole del bene e del male già scritte. |
| Il backtest non è la realtà | Un modello che funziona sui dati storici quasi sempre smette di funzionare live. L'unico dato che conta è il paper trading out-of-sample su almeno 6 mesi e diversi regimi di mercato. |
| Il sistema suggerisce, l'utente decide | Nessun ordine automatico su soldi reali. Ogni operazione reale viene approvata manualmente fino a quando il sistema non ha almeno 12 mesi di track record positivo e verificato. |
| Scala quando funziona | Ogni aumento di complessità — più titoli, più sensi, modello più profondo — si aggiunge solo se lo stadio precedente ha dimostrato di funzionare con metriche misurabili e stabili. |

---

## 11. Come usare questo documento nelle sessioni future

Questo documento è la memoria del progetto. Claude AI non ricorda le conversazioni precedenti — ogni nuova chat riparte da zero. Per continuare il lavoro senza perdere nulla, seguire questa procedura all'inizio di ogni sessione:

1. Aprire una nuova chat con Claude.
2. Caricare questo documento come allegato oppure incollare il contenuto rilevante.
3. Scrivere: *"Questo è il documento del progetto AI Market Predictor. Siamo arrivati fino a [punto X]. Oggi vogliamo lavorare su [obiettivo della sessione]."*
4. Claude rilegge il documento e riparte esattamente dal punto in cui ci si era fermati.

Il documento va aggiornato alla fine di ogni sessione di lavoro significativa — ogni volta che si definisce qualcosa di nuovo, si prende una decisione tecnica, o si completa uno stadio. In questo modo la memoria del progetto cresce insieme al sistema.

---

## 12. Stato del progetto — Fase 1 COMPLETATA (giugno 2026)

> Questa sezione è stata aggiunta al termine della Fase 1 per registrare quanto realizzato.

La **Fase 1 — Fondamenta** è completa. Tutto gira in locale sul Mac, come previsto. Il mondo in cui il sistema nascerà esiste, è stato verificato con i propri occhi, ed è pulito.

**Cosa è stato costruito:**

- **Universo titoli definito**: 66 ticker, 6 per ciascuno degli 11 settori S&P500.
- **Storico scaricato**: 3.508.587 candele a 15 minuti, 5 anni (giugno 2021 → giugno 2026), da Polygon.io.
- **Indicatori calcolati** su ogni candela: RSI, MACD, EMA 20/50/200, Bollinger Bands, ATR, pattern doji.
- **Database DuckDB** (~759 MB) con tre tabelle: `candles`, `macro`, `download_log`.
- **Dati macro** scaricati da FRED (VIX, Fed rate, CPI, disoccupazione) — 1.826 giorni — in vista dello Stadio 3.
- **Dataset di training** assemblato (`dataset.parquet`, ~426 MB): candele + macro + target `return_next`.
- **Qualità verificata**: controlli base e approfonditi (8 categorie). 0 problemi critici.
- **Dashboard interattiva** (Plotly/Dash) con timeframe adattivo: grafici candlestick, RSI/MACD, heatmap settoriale, crescita settori nel tempo, stato database.

**Scoperta rilevante durante la verifica** — proprio guardando i grafici, come prescrive il metodo: il ticker **META** conteneva dati di un'altra azienda prima del 2022-06-09 (Facebook ha tradato come "FB" fino a quella data). I dati sporchi sono stati rimossi e gli indicatori ricalcolati. È l'unico dei 66 titoli con questo problema. Questo conferma il valore del Passo di verifica visiva: *un grafico ti dice immediatamente se qualcosa non va.*

**Il prossimo passo definito**: inizio della **Fase 2 — Training**. Costruzione dell'ambiente di Reinforcement Learning e avvio dello **Stadio 1 (Vedere)**. La decisione più delicata — la definizione della ricompensa — verrà presa qui, con i primi dati reali davanti, esattamente come previsto dalla filosofia del progetto.

---

*Documento generato con Claude AI · AI Market Predictor Project · Versione 4.0*
