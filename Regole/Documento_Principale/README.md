# AI MARKET PREDICTOR

### Versione 4.0 — Architettura e memoria del progetto

**Un trader artificiale che impara come un bambino**

---

## Scheda riassuntiva del progetto

| Parametro                   | Valore                                                                                                  |
| --------------------------- | ------------------------------------------------------------------------------------------------------- |
| Obiettivo                   | Trader artificiale che impara da solo attraverso rinforzo — non viene programmato, viene fatto crescere |
| Universo titoli             | 60-80 titoli — 5-7 per ciascuno degli 11 settori S&P500                                                 |
| Frequenza candele           | 15 minuti                                                                                               |
| Anni di storia              | 5-7 anni (almeno 2 cicli completi di mercato)                                                           |
| Meccanismo di apprendimento | Reinforcement Learning — il mercato è il maestro, la ricompensa è l'unica guida                         |
| Stadi di apprendimento      | 4 stadi in sequenza: Vedere → Associare → Contestualizzare → Sentire                                    |
| Notizie                     | Introdotte in tempo reale solo dallo Stadio 4 — vissute, non studiate dallo storico                     |
| Claude API                  | Sistema emotivo sulle notizie (da -1 a +1) + analisi errori settimanale                                 |
| Ricompensa                  | Da definire nella fase di costruzione con i primi dati reali davanti                                    |
| Conoscenza del dominio      | Fornita da Claude AI — il sistema non parte da zero sul trading                                         |
| Costo mensile a regime      | ~45-55 euro/mese                                                                                        |
| Prima esposizione reale     | Solo dopo 6 mesi di paper trading positivi con tutte e 4 le metriche superate                           |

---

## 1. Filosofia — Il bambino che impara

Questo sistema non viene programmato per fare trading. Viene fatto crescere.

Un bambino non nasce sapendo cosa è pericoloso e cosa è sicuro. Osserva il mondo, tocca le cose, riceve segnali — si brucia, sorride, cade, ride. Nel tempo costruisce una mappa sempre più precisa di come funziona la realtà. Non gli viene spiegato tutto in anticipo — impara vivendo.

Il sistema funziona allo stesso modo. Nasce con i dati grezzi del mercato — prezzi, volumi, candele. Non sa ancora cosa significa un pattern rialzista o ribassista. Lo scopre lui, attraverso il ciclo continuo di osservazione, azione e ricompensa.

La conoscenza del trading — i principi, le regole, la logica dei mercati — viene fornita da Claude AI e costruita insieme nel tempo. Il sistema non parte da zero su questo: ha già accesso a una base di conoscenza che cresce ad ogni sessione di lavoro. Ciò che invece deve scoprire da solo è come quella conoscenza si applica ai dati reali, in tempo reale, con la ricompensa del mercato come unico giudice.

### Il ciclo fondamentale

| Fase              | Cosa succede nel sistema                                                        | Parallelo con il bambino                                        |
| ----------------- | ------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| Osserva           | Riceve i dati di mercato — candele, volumi, indicatori, movimenti settoriali    | Il bambino vede il mondo intorno a sé                           |
| Riconosce         | Identifica una forma, una struttura, un pattern nei dati                        | Il bambino riconosce una forma o una situazione familiare       |
| Agisce            | Fa una previsione — questo titolo salirà o scenderà                             | Il bambino tocca, prova, sperimenta                             |
| Riceve ricompensa | Il mercato risponde — aveva ragione o torto? La ricompensa rinforza o corregge  | Il bambino si brucia oppure sorride                             |
| Impara            | Aggiorna il suo comportamento per il ciclo successivo — è leggermente più bravo | Il bambino non tocca più il fuoco — o ripete ciò che funzionava |

Questo meccanismo si chiama Reinforcement Learning. Non gli diciamo cosa cercare — lo lasciamo scoprire. Il mercato è il maestro. La ricompensa è l'unica guida.

---

## 2. Il mondo in cui il sistema nasce — I dati

Il sistema nasce dentro un mondo preciso. Quel mondo è costruito con dati reali di mercato, organizzati in modo che il sistema possa imparare a leggerli progressivamente, un livello alla volta.

### 2.1 I titoli — divisi per settore

Il sistema non analizza tutti i titoli allo stesso modo. Li vede come famiglie — gruppi di aziende che si muovono in modo correlato, che reagiscono agli stessi eventi, che rappresentano pezzi diversi dell'economia reale.

Questa divisione settoriale è fondamentale: insegna al sistema che il mercato non è un insieme caotico di prezzi, ma un ecosistema con struttura. Quando un settore si muove, spesso trascina o anticipa altri settori. Le rotazioni settoriali — denaro che esce dal tech ed entra nelle utilities, o viceversa — sono tra i movimenti più prevedibili e ricorrenti del mercato. Il sistema le imparerà nello Stadio 3.

| Settore                | Titoli rappresentativi       | Caratteristica chiave                                  |
| ---------------------- | ---------------------------- | ------------------------------------------------------ |
| Technology             | AAPL, MSFT, NVDA, AMD, GOOGL | Guida spesso i movimenti dell'intero mercato           |
| Financials             | JPM, BAC, GS, MS, BRK.B      | Sensibile ai tassi di interesse e al ciclo del credito |
| Health Care            | JNJ, UNH, PFE, ABBV, MRK     | Difensivo — regge nei mercati in ribasso               |
| Consumer Discretionary | AMZN, TSLA, HD, MCD, NKE     | Ciclico — riflette la fiducia dei consumatori          |
| Consumer Staples       | PG, KO, PEP, WMT, COST       | Difensivo — prodotti di prima necessità                |
| Energy                 | XOM, CVX, COP, SLB, EOG      | Correlato al prezzo del petrolio e alla geopolitica    |
| Industrials            | CAT, BA, HON, UPS, GE        | Indicatore del ciclo economico globale                 |
| Materials              | LIN, APD, NEM, FCX, ECL      | Sensibile all'inflazione e alla domanda globale        |
| Real Estate            | AMT, PLD, CCI, EQIX, SPG     | Sensibile ai tassi — si comporta come le obbligazioni  |
| Utilities              | NEE, DUK, SO, AEP, EXC       | Difensivo — domanda stabile indipendente dal ciclo     |
| Communication Services | META, NFLX, DIS, CMCSA, T    | Mix tra growth tecnologico e media tradizionale        |

### 2.2 Le candele a 15 minuti — la lingua del sistema

Ogni candela a 15 minuti è una parola nel linguaggio che il sistema sta imparando. Contiene quattro informazioni: il prezzo di apertura, il massimo, il minimo, e il prezzo di chiusura. Più il volume — quante azioni sono cambiate di mano in quel periodo.

La scelta di 15 minuti è deliberata. I 5 minuti hanno troppo rumore — movimenti casuali che non significano nulla. I 30 minuti perdono dettaglio sui movimenti intraday importanti. I 15 minuti sono il punto di equilibrio: abbastanza reattivi da catturare i segnali reali, abbastanza filtrati da ridurre il rumore.

Con 5-7 anni di storia a 15 minuti, ogni titolo accumula circa 100.000-140.000 candele. È la base statistica necessaria perché il sistema possa distinguere i pattern ricorrenti dal caso puro.

### 2.3 Gli indicatori tecnici — i sensi del bambino

Il sistema non vede solo i prezzi grezzi. Ha sensi aggiuntivi che gli permettono di percepire aspetti del mercato non visibili a occhio nudo su una singola candela.

| Indicatore      | Cosa misura                                                     | Cosa insegna al sistema                                                        |
| --------------- | --------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| RSI             | Velocità e forza del movimento dei prezzi — scala da 0 a 100    | Quando un titolo è in ipercomprato (>70) o ipervenduto (<30)                   |
| MACD            | Differenza tra due medie mobili — segnala cambi di momentum     | Quando la forza di un trend sta cambiando direzione                            |
| EMA 20/50/200   | Medie mobili esponenziali su diversi orizzonti temporali        | La tendenza di breve, medio e lungo periodo del titolo                         |
| Bollinger Bands | Volatilità del titolo rispetto alla sua media storica           | Quando il prezzo si espande o contrae rispetto al suo comportamento normale    |
| ATR             | Average True Range — ampiezza media dei movimenti in un periodo | Quanto si muove tipicamente quel titolo — utile per calibrare la ricompensa    |
| Volume          | Quante azioni sono cambiate di mano in quella candela           | Se un movimento è supportato da partecipazione reale o è debole e inaffidabile |
| Pattern candele | 60+ formazioni visive riconoscibili nelle candele giapponesi    | Segnali di inversione o continuazione codificati dalla tradizione tecnica      |

> La tabella sopra mostra i **sensi fondamentali**, quelli con cui il progetto è partito. Dalla fine della Fase 1 il sistema ne ha molti di più: **45 indicatori** raggruppati in sei famiglie — momentum (RSI, Stocastico, ROC, Williams %R, CCI), direzione del trend (MACD, EMA, Parabolic SAR, Aroon), forza del trend (ADX), volatilità (Bollinger, ATR, Donchian, Keltner), volume (OBV, MFI, CMF, Force Index) e Ichimoku — più **9 pattern candele** selezionati tra le formazioni classiche. L'elenco completo, con la spiegazione operativa di ciascuno, è consultabile nel glossario della dashboard. Più sensi significano una percezione più ricca del mercato; quali contino davvero lo deciderà il sistema attraverso la ricompensa, non noi in anticipo.

---

## 3. Come il sistema impara — Reinforcement Learning

### 3.1 Il meccanismo di ricompensa

Il cuore del sistema è la ricompensa. Ogni volta che il sistema fa una previsione, il mercato gli risponde. Quella risposta è la ricompensa — positiva se aveva ragione, negativa se aveva torto. Nel tempo il sistema impara a fare previsioni sempre più accurate per massimizzare la ricompensa cumulativa.

La definizione precisa della ricompensa — quanto movimento, in quante candele, con quale soglia — è la decisione più delicata di tutto il progetto. Non viene definita adesso. Viene definita nella fase di costruzione, quando i primi dati reali sono davanti agli occhi e si può osservare come si comporta il sistema con diverse configurazioni.

Nota importante: definire la ricompensa troppo presto, senza dati reali, rischia di costruire un sistema che ottimizza la metrica sbagliata. Un bambino non nasce con le regole del bene e del male già scritte — le scopre vivendo. Faremo lo stesso.

### 3.2 I 4 stadi di apprendimento — dal semplice al complesso

Il sistema non impara tutto insieme. Come un bambino, sviluppa le competenze in ordine di complessità crescente. Ogni stadio costruisce sulla base del precedente. Non si passa allo stadio successivo senza che quello corrente sia stabile e misurabile.

| Stadio | Nome             | Cosa impara                                                                                                                                                                                                                                                            | Come si misura                                                                                                                                                                       | Condizione per avanzare                                         |
| ------ | ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------- |
| 1      | Vedere           | Riconosce le forme dei grafici. Distingue un trend rialzista da uno ribassista. Identifica supporti, resistenze, e le strutture di base del movimento dei prezzi.                                                                                                      | Il sistema descrive correttamente la struttura del grafico che sta guardando, in modo stabile e coerente su più titoli diversi.                                                      | Coerenza stabile su più titoli e periodi                        |
| 2      | Associare        | Collega i pattern ai movimenti successivi. Impara che certi setup sono stati seguiti più spesso da rialzi, altri da ribassi. Inizia a fare previsioni e ricevere ricompensa.                                                                                           | Accuracy direzionale superiore al 50% su dati non visti prima durante l'addestramento.                                                                                               | Accuracy stabile sopra il 53% out-of-sample                     |
| 3      | Contestualizzare | Impara che lo stesso pattern in un settore forte si comporta diversamente rispetto a un settore debole. Scopre le rotazioni settoriali — denaro che esce dal tech ed entra nelle utilities. Vede i titoli come membri di famiglie, non come entità isolate.            | Performance migliorata rispetto allo Stadio 2 quando usa il contesto settoriale. Se togliendo l'informazione settoriale le performance peggiorano, il sistema la sta usando davvero. | Miglioramento misurabile su paper trading con contesto vs senza |
| 4      | Sentire          | Inizia a ricevere le notizie in tempo reale. Impara lentamente la correlazione tra il sentiment delle notizie e i movimenti successivi dei prezzi. Questo senso si sviluppa solo dopo che i primi tre stadi sono solidi — esattamente come le emozioni per un bambino. | Le previsioni migliorano in modo misurabile quando include il sentiment delle notizie rispetto a quando non lo include.                                                              | Miglioramento misurabile con notizie vs senza notizie           |

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

| Fase                        | Relazione con le notizie                                                                                                                                                                                                                                                                                                            |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Stadi 1-3                   | Il sistema non vede le notizie. Impara solo dai dati tecnici. Questo è deliberato — serve costruire una base solida prima di aggiungere la complessità del linguaggio e del contesto delle news.                                                                                                                                    |
| Ingresso notizie (Stadio 4) | Quando lo Stadio 3 è stabile, il sistema inizia a ricevere le notizie in tempo reale — solo da quel momento in poi. Non vengono usati archivi storici di notizie. Il sistema le vive, non le studia a ritroso. Questo è fondamentale: le notizie devono essere un'esperienza vissuta, non un'informazione retrospettiva.            |
| Apprendimento emotivo       | Il sistema osserva cosa succede ai prezzi dopo ogni notizia che riceve. Nel tempo costruisce da solo la correlazione — questo tipo di notizia tende ad amplificare i movimenti rialzisti, quest'altro li smorza. Non glielo insegniamo noi — lo scopre attraverso la ricompensa.                                                    |
| Ruolo di Claude             | Claude legge ogni notizia e la traduce in un valore numerico di sentiment da -1 (molto negativo) a +1 (molto positivo). Questo valore entra come input aggiuntivo nel sistema accanto ai dati tecnici. Claude porta la conoscenza del linguaggio e del contesto — il sistema porta l'esperienza accumulata di cosa è successo dopo. |

---

## 5. Claude API — due ruoli distinti

Claude API non è uno strumento di reporting. Ha due ruoli precisi nel sistema, attivi in momenti e con obiettivi diversi.

| Ruolo                         | Quando                                                | Input                                                                                              | Output                                                                                                                                     |
| ----------------------------- | ----------------------------------------------------- | -------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| Sistema emotivo sulle notizie | In tempo reale, dallo Stadio 4 in poi                 | Notizie delle ultime ore per il titolo o il settore che il sistema sta analizzando in quel momento | Valore sentiment da -1 a +1 che entra come input aggiuntivo nel modello accanto ai dati tecnici                                            |
| Analisi errori settimanale    | Una volta a settimana, da subito — da tutti gli stadi | Log degli ultimi 7 giorni: segnali emessi, risultati reali, pattern di errore sistematici          | Dove il sistema sbaglia sistematicamente? In quali condizioni di mercato i segnali sono inaffidabili? Suggerimenti per il ciclo successivo |

Questa struttura mantiene il costo API basso e il valore alto. Claude interviene solo dove la comprensione del linguaggio e del contesto cambia davvero la qualità dell'informazione — non per generare testo descrittivo che il sistema potrebbe produrre da solo con calcoli numerici.

---

## 6. Validazione — come sappiamo se funziona

Il sistema non viene mai considerato pronto per soldi reali basandosi su sensazioni o su risultati sui dati storici. Esistono quattro metriche precise che devono essere superate tutte e quattro su dati out-of-sample. Non ci sono eccezioni.

| Metrica               | Soglia minima        | Perché questa soglia                                                                                                                                                                                             |
| --------------------- | -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Accuracy direzionale  | > 53% out-of-sample  | Il 50% è un lancio di moneta. Servono almeno 3 punti percentuali di edge reale per coprire i costi operativi e giustificare il rischio aggiuntivo rispetto al non fare nulla.                                    |
| Sharpe ratio          | > 1.0 su 6 mesi      | Misura la qualità del rendimento, non solo la quantità. Un sistema che guadagna il 10% con volatilità altissima è peggiore di uno che guadagna il 6% con stabilità. Sopra 1.0 è accettabile, sopra 2.0 è ottimo. |
| Drawdown massimo      | < 20%                | Sopra il 20% di perdita dal picco, diventa psicologicamente impossibile continuare a seguire il sistema. La disciplina crolla prima dei soldi. Il sistema deve essere sostenibile anche emotivamente.            |
| Confronto vs Buy&Hold | Superiore su 2+ anni | Se il sistema non batte la strategia passiva di comprare l'indice e aspettare, non vale la complessità, il tempo e il rischio aggiuntivo che introduce. È il benchmark minimo di utilità.                        |

---

## 7. Paper trading — 6 mesi obbligatori

Il paper trading non è una formalità. È l'unico modo per sapere se il sistema funziona nel mondo reale, fuori dai dati storici su cui ha imparato. Un modello che funziona benissimo sui dati passati quasi sempre smette di funzionare quando il mercato cambia regime.

Durata minima: 6 mesi. Non si abbrevia per nessun motivo, nemmeno se i risultati sembrano ottimi nelle prime settimane. Servono diversi regimi di mercato — rialzo, laterale, ribasso, alta volatilità — per avere evidenza statistica reale e non illudersi con un momento favorevole.

| Periodo  | Obiettivo                                                                                                                                                                    | Criterio per avanzare                                                                                             |
| -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| Mesi 1-2 | Setup del simulatore. Prime operazioni virtuali. Verifica che i segnali siano coerenti con la logica attesa. Identificazione dei primi bug e anomalie.                       | Pipeline stabile. Nessun errore critico. Dati puliti e continui per almeno 4 settimane consecutive.               |
| Mesi 3-4 | Raccolta sistematica delle metriche. Identificazione dei pattern di errore con analisi Claude settimanale. Prime ottimizzazioni basate su evidenza reale, non su intuizioni. | Accuracy superiore al 53%. Comportamento stabile in diversi contesti di mercato — non solo in mercati favorevoli. |
| Mesi 5-6 | Analisi completa: Sharpe, drawdown, confronto Buy&Hold. Revisione approfondita dei log errori con Claude. Decisione informata e basata su dati reali sul passo successivo.   | Tutte e quattro le metriche superate. Solo allora si valuta la prima esposizione reale.                           |

Alla fine dei 6 mesi esistono tre scenari. Risultati ottimi: prima esposizione reale con 200-500 euro massimo e stop loss obbligatori su ogni posizione. Risultati misti: altri 3 mesi di ottimizzazione mirata. Risultati negativi: si torna allo stadio di apprendimento precedente e si identifica il problema prima di riprendere.

---

## 8. Stack tecnologico

| Componente         | Tecnologia             | Costo         | Ruolo nel sistema                                                                         |
| ------------------ | ---------------------- | ------------- | ----------------------------------------------------------------------------------------- |
| Server H24         | Hetzner CX32           | 8 euro/mese   | Esegue tutto in autonomia senza Mac acceso — il sistema lavora anche di notte             |
| Dati mercato       | Polygon.io Starter     | ~27 euro/mese | Candele 15min live e storiche su tutti i titoli + notizie per titolo e settore            |
| Database           | DuckDB                 | Gratuito      | Gestisce milioni di righe di candele storiche con query analitiche veloci                 |
| Indicatori tecnici | pandas-ta + TA-Lib     | Gratuito      | 45 indicatori (momentum, trend, volatilità, volume, Ichimoku) + 9 pattern candele giapponesi |
| Dati macro         | FRED API               | Gratuito      | Fed, CPI, NFP, earnings calendar — il contesto macro per ogni periodo storico e live      |
| Cervello AI        | Claude API (Anthropic) | ~10 euro/mese | Sentiment notizie da -1 a +1 in tempo reale + analisi errori settimanale sui log          |
| Modello RL         | PyTorch + algoritmo RL | Gratuito      | Il cervello che impara attraverso i 4 stadi — si costruisce e si raffina progressivamente |
| Dashboard          | Plotly / Python        | Gratuito      | Grafici live, heatmap settoriale, metriche paper trading, log errori visualizzati         |
| Linguaggio         | Python                 | Gratuito      | Standard de facto per ML e analisi dati — tutte le librerie necessarie sono disponibili   |

---

## 9. Costi mensili

Soldi esposti al mercato: zero fino alla fine del paper trading. Prima esposizione reale: 200-500 euro massimo, con stop loss obbligatori su ogni posizione. Il sistema suggerisce — l'utente approva ogni operazione manualmente per almeno i primi 12 mesi.

| Voce               | Stadi 1-3    | Stadio 4 + paper trading | Sistema completo       |
| ------------------ | ------------ | ------------------------ | ---------------------- |
| Hetzner server     | 8 euro       | 8 euro                   | 18 euro (upgrade CX42) |
| Polygon.io         | ~27 euro     | ~27 euro                 | ~27 euro               |
| Claude API         | ~5 euro      | ~10 euro                 | ~10 euro               |
| Tutto il resto     | 0 euro       | 0 euro                   | 0 euro                 |
| **Totale mensile** | **~40 euro** | **~45 euro**             | **~55 euro**           |

---

## 10. Principi operativi — le regole che non cambiano

| Principio                                | Regola concreta                                                                                                                                                                             |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Il sistema impara, non viene programmato | Non si codificano regole di trading nel modello. Si crea l'ambiente di apprendimento e si lascia che il sistema scopra i pattern da solo attraverso il ciclo osserva-agisce-ricompensa.     |
| Un stadio alla volta                     | Non si passa allo stadio successivo senza che quello corrente abbia dimostrato di funzionare con metriche misurabili. La fretta produce sistemi che sembrano funzionare ma non funzionano.  |
| Un senso alla volta                      | Le notizie entrano solo dopo che i pattern tecnici degli Stadi 1-3 sono appresi in modo stabile. Aggiungere complessità prima che la base sia solida produce confusione, non miglioramento. |
| La ricompensa si definisce con i dati    | Il meccanismo di ricompensa viene definito quando i primi dati reali sono disponibili — non in anticipo. Un bambino non nasce con le regole del bene e del male già scritte.                |
| Il backtest non è la realtà              | Un modello che funziona sui dati storici quasi sempre smette di funzionare live. L'unico dato che conta è il paper trading out-of-sample su almeno 6 mesi e diversi regimi di mercato.      |
| Il sistema suggerisce, l'utente decide   | Nessun ordine automatico su soldi reali. Ogni operazione reale viene approvata manualmente fino a quando il sistema non ha almeno 12 mesi di track record positivo e verificato.            |
| Scala quando funziona                    | Ogni aumento di complessità — più titoli, più sensi, modello più profondo — si aggiunge solo se lo stadio precedente ha dimostrato di funzionare con metriche misurabili e stabili.         |

---

## 11. Come usare questo documento nelle sessioni future

Questo documento è la memoria del progetto. Claude AI non ricorda le conversazioni precedenti — ogni nuova chat riparte da zero. Per continuare il lavoro senza perdere nulla, seguire questa procedura all'inizio di ogni sessione:

1. Aprire una nuova chat con Claude.
2. Caricare questo documento come allegato oppure incollare il contenuto rilevante.
3. Scrivere: _"Questo è il documento del progetto AI Market Predictor. Siamo arrivati fino a [punto X]. Oggi vogliamo lavorare su [obiettivo della sessione]."_
4. Claude rilegge il documento e riparte esattamente dal punto in cui ci si era fermati.

Il documento va aggiornato alla fine di ogni sessione di lavoro significativa — ogni volta che si definisce qualcosa di nuovo, si prende una decisione tecnica, o si completa uno stadio. In questo modo la memoria del progetto cresce insieme al sistema.

---

## 12. Fase 2 — Training: architettura e decisioni chiave

> Questa sezione documenta le decisioni architetturali prese prima di iniziare la Fase 2, al termine della sessione di progettazione di giugno 2026. Ogni scelta ha una ragione precisa — è importante tenerla scritta per non doverla ridiscutere in futuro.

### Il ritmo del sistema: ogni 15 minuti, non ogni secondo

Il sistema riceve i dati del mercato ogni **15 minuti** — alla chiusura di ogni candela, non ogni secondo. Questa scelta è deliberata e non è un compromesso: è la decisione giusta.

Al secondo, il 99% del movimento dei prezzi è rumore casuale — micro-ordini, rimbalzi tra domanda e offerta, fluttuazioni senza significato. Il segnale reale (la direzione, il momentum, il pattern) è sepolto dentro quel rumore. Dare al sistema dati al secondo è come far leggere un libro lettera per lettera, una al secondo: vede tutto, ma non capisce più la frase.

La candela a 15 minuti non butta via i secondi — li riassume in 5 numeri significativi: apertura, massimo, minimo, chiusura, volume. Si tiene l'essenza, si elimina il rumore. I trader professionisti più capaci non guardano ogni tick — leggono le strutture a 15 minuti, 1 ora, 4 ore. Il sistema impara la stessa cosa.

L'HFT (trading al secondo) è un altro sport: richiederebbe latenze di microsecondi, server fisicamente attaccati alle borse, e un piano dati che costa centinaia di euro al mese. Non è la nostra partita, e non deve esserlo.

Quando il sistema vede un segnale e invia un ordine al broker, l'esecuzione avviene in **millisecondi** — indipendentemente dal fatto che il segnale arrivi ogni 15 minuti. Il ritmo di pensiero è a 15 minuti; la velocità di azione è istantanea. Non c'è conflitto.

**Il piano per il futuro**: se e quando la versione a 15 minuti avrà dimostrato di funzionare con tutte le metriche superate, si valuta di scendere a 5 minuti o 1 minuto. Niente prima. "Scala quando funziona" — non quando sembra un'idea migliore.

---

### Come il sistema impara a vedere — il VQ-VAE

Lo Stadio 1 si chiama "Vedere" per una ragione precisa: il sistema deve imparare a riconoscere le **strutture** dei grafici prima di poter fare qualsiasi previsione. Per farlo usiamo un'architettura specifica chiamata **VQ-VAE** (Vector Quantized Variational Autoencoder). Il nome è tecnico, il concetto è semplice.

Immagina di mostrare al bambino migliaia di grafici — rialzi, ribassi, laterali, rotture, rimbalzi — senza dirgli nulla. Il bambino non sa ancora cosa sia un "testa-spalle" o una "bandiera rialzista". Ma nel tempo inizia a notare: _"questi grafici si assomigliano, questi altri sono diversi"_. Comincia a raggruppare le forme anche senza un nome per loro.

Il VQ-VAE funziona esattamente così:

1. **Comprime** ogni finestra di candele (le ultime N candele con tutti gli indicatori) in un piccolo vettore di numeri — la "firma" di quella struttura.
2. **Quantizza** quella firma scegliendo il codice più simile da un dizionario interno (il "codebook") — come arrotondare a una parola tra un vocabolario limitato.
3. **Ricostruisce** la finestra originale partendo dal codice scelto.
4. **Impara** minimizzando l'errore di ricostruzione — più il codebook è preciso, meglio ricostruisce, e quindi più ha capito le strutture.

Il risultato finale è un **codebook di pattern**: un catalogo di forme fondamentali del mercato, scoperte autonomamente dai dati, senza che nessuno abbia scritto "questo è un doppio massimo" o "questo è un supporto".

---

### La memoria dei pattern — una libreria che cresce

Il codebook non è solo un risultato interno del modello. È una **memoria visiva** del sistema, leggibile e modificabile.

Ogni voce del codebook è un vettore numerico che rappresenta una forma tipica. Questi vettori vengono salvati in una cartella dedicata (`models/pattern_memory/`). Possono essere visualizzati come grafici — così è possibile guardare cosa il sistema ha imparato a "vedere".

La cosa più potente: questa memoria **si può arricchire**. Se si prende un libro di analisi tecnica e si estraggono esempi di pattern classici — testa-spalle, doppio massimo, bandiera — questi possono essere aggiunti al codebook come vettori aggiuntivi. Il sistema non li applica come regole rigide: li tratta come qualsiasi altro pattern in memoria. Se nei dati reali quel pattern ha portato a movimenti significativi, il sistema lo userà. Se non ha funzionato, lo ignorerà. Il mercato rimane il giudice.

Questo approccio non viola la filosofia del progetto — anzi, la rispetta. Non stiamo scrivendo regole ("se vedi testa-spalle, vendi"). Stiamo arricchendo il vocabolario di partenza. L'esperienza vissuta decide cosa funziona.

La memoria cresce nel tempo: nuovi pattern scoperti live, pattern da libri aggiunti manualmente, pattern validati dallo Stadio 2 che si dimostrano predittivi. Non è una scatola nera — è una libreria che si può aprire, guardare, e modificare.

---

### Il piano per i sensi successivi

Lo Stadio 1 è costruito per essere **la base di tutto il resto**. L'occhio — l'encoder VQ-VAE — rimane lo stesso in tutti gli stadi. Su di esso si costruisce in sequenza:

| Stadio               | Cosa si aggiunge                                                          | Quando                |
| -------------------- | ------------------------------------------------------------------------- | --------------------- |
| 1 — Vedere           | L'occhio VQ-VAE + la memoria dei pattern                                  | Adesso — Fase 2       |
| 2 — Associare        | Una "testa" decisionale sopra l'occhio: pattern → previsione + ricompensa | Dopo Stadio 1 stabile |
| 3 — Contestualizzare | Multi-timeframe (5 min, 1 ora, 4 ore) + contesto settoriale               | Dopo Stadio 2 stabile |
| 4 — Sentire          | Claude API sentiment sulle notizie live                                   | Dopo Stadio 3 stabile |

Il multi-timeframe entra **allo Stadio 3**, non prima. La ragione: imparare su un solo timeframe prima è più semplice e produce un fondamento più solido. Aggiungere 1 minuto, 5 minuti e 1 ora al sistema che già sa vedere a 15 minuti è un'estensione naturale. Aggiungere tutto insieme dall'inizio è confusione, non apprendimento.

**Principio invariante**: un senso alla volta. Ogni aggiunta viene valutata confrontando la performance con e senza di essa. Se il nuovo senso non migliora le metriche in modo misurabile, non entra nel sistema.

---

## 13. Stato del progetto — Fase 1 COMPLETATA (giugno 2026)

> Questa sezione è stata aggiunta al termine della Fase 1 per registrare quanto realizzato.

La **Fase 1 — Fondamenta** è completa. Tutto gira in locale sul Mac, come previsto. Il mondo in cui il sistema nascerà esiste, è stato verificato con i propri occhi, ed è pulito.

**Cosa è stato costruito:**

- **Universo titoli definito**: 66 ticker, 6 per ciascuno degli 11 settori S&P500.
- **Storico scaricato**: 3.508.585 candele a 15 minuti, 5 anni (giugno 2021 → giugno 2026), da Polygon.io.
- **Indicatori calcolati** su ogni candela: 45 indicatori tecnici in sei famiglie (momentum, direzione e forza del trend, volatilità, volume, Ichimoku) + 9 pattern candele. La tabella `candles` ha 56 colonne.
- **Database DuckDB** (~1.6 GB) con tre tabelle: `candles`, `macro`, `download_log`.
- **Dati macro** scaricati da FRED (VIX, Fed rate, CPI, disoccupazione) — 1.826 giorni — in vista dello Stadio 3.
- **Dataset di training** assemblato (`dataset.parquet`, ~426 MB): candele + macro + target `return_next`.
- **Qualità verificata**: controlli base e approfonditi (8 categorie). 0 problemi critici.
- **Dashboard interattiva** (Plotly/Dash), ricostruita come software modulare con 7 schermate: grafico candlestick, scheda completa di ogni titolo con tutti gli indicatori componibili, confronto di un indicatore tra i titoli di un settore, heatmap settoriale, crescita settori nel tempo, glossario degli indicatori, stato database.
- **Progetto riorganizzato** in tre mondi indipendenti su un core comune (`shared/`): `data_pipeline/` (costruzione del database), `dashboard/` (visualizzazione), `training/` (Fase 2). Ognuno con il proprio README.

**Scoperta rilevante durante la verifica** — proprio guardando i grafici, come prescrive il metodo: il ticker **META** conteneva dati di un'altra azienda prima del 2022-06-09 (Facebook ha tradato come "FB" fino a quella data). I dati sporchi sono stati rimossi e gli indicatori ricalcolati. È l'unico dei 66 titoli con questo problema. Questo conferma il valore del Passo di verifica visiva: _un grafico ti dice immediatamente se qualcosa non va._

**Il prossimo passo definito**: inizio della **Fase 2 — Training**. Costruzione dell'ambiente di Reinforcement Learning e avvio dello **Stadio 1 (Vedere)**. La decisione più delicata — la definizione della ricompensa — verrà presa qui, con i primi dati reali davanti, esattamente come previsto dalla filosofia del progetto.

---
