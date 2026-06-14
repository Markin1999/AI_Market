# 🗂️ Guida alle cartelle e ai file — AI Market Predictor

Mappa completa del progetto: **ogni cartella, sottocartella e file**, con la spiegazione di cosa fa e perché esiste.
Aggiornato dopo la divisione in `shared/`, `data_pipeline/`, `dashboard/`, `training/`.

---

## Vista d'insieme

Il progetto è diviso in **tre mondi** che condividono un **core comune**:

```
ai_market_predictor/
│
├── shared/              # CORE CONDIVISO — usato da tutti i mondi
├── data_pipeline/       # MONDO 1 — scarica da Polygon e costruisce il database
├── dashboard/           # MONDO 2 — software di visualizzazione (grafici)
├── training/            # MONDO 3 — le due IA: occhio (vede) + predittore (prevede)
│
├── data/                # Database e dataset (file pesanti, fuori da GitHub)
├── models/              # Modelli addestrati + libreria dei pattern (Fase 2)
├── logs/                # Log delle operazioni
├── notebooks/           # Jupyter notebook per analisi libere
│
├── Regole/              # Documenti del progetto (visione, roadmap)
│
├── README.md                    # Documentazione principale del progetto
├── readmeIstruzioniAvvio.md     # Guida pratica: quali comandi lanciare
├── readme_Istruzioni_cartelle.md  # QUESTO file: cosa contiene ogni cartella
├── DuckDB.session.sql           # Query SQL pronte per esplorare il DB
└── .gitignore                   # Cosa git deve ignorare
```

**Le tre regole d'oro della struttura:**
1. `shared/` contiene ciò che **tutti i mondi devono condividere** (config + calcolo indicatori). Una copia sola, mai duplicata, così non divergono.
2. I comandi si lanciano **sempre dalla cartella principale** (la root), perché gli script trovano `shared/` e `data/` partendo da lì.
3. I file pesanti (`data/`, `models/`) e i segreti (`.env`) **non vanno su GitHub**.

**I tre mondi sono indipendenti:** la pipeline scrive il database, la dashboard lo legge per mostrare grafici, il training lo legge per imparare. Ognuno ha il suo README.

---

## 📦 shared/ — il core condiviso

Il cuore comune. Sia la pipeline dati sia il training importano da qui. Se cambi un indicatore o la lista titoli, lo cambi **una volta sola** e vale per tutti.

| File | Cosa fa |
|---|---|
| `shared/__init__.py` | File vuoto che rende `shared` un pacchetto Python importabile. Non si tocca. |

### shared/config/ — configurazione e segreti

| File | Cosa fa |
|---|---|
| `settings.py` | **Il file di configurazione centrale.** Contiene: le API key (lette dal `.env`), l'universo dei 66 titoli (`TICKERS_BY_SECTOR`, `ALL_TICKERS`, `TICKER_TO_SECTOR`), i percorsi (`DB_PATH`, `PARQUET_PATH`), i parametri delle candele (`CANDLE_MULTIPLIER = 15`, `HISTORY_YEARS = 5`) e i parametri degli indicatori (RSI, EMA, MACD, Bollinger, ATR). Tutti gli script importano da qui invece di avere valori scritti a caso. |
| `.env` | **I segreti: le tue API key** (`POLYGON_API_KEY`, `FRED_API_KEY`). ⛔ NON va mai su GitHub — è in `.gitignore`. Se lo perdi, le rigeneri dai siti di Polygon e FRED. |
| `__init__.py` | Marker di pacchetto. Non si tocca. |

### shared/indicators/ — calcolo degli indicatori

| File | Cosa fa |
|---|---|
| `calculate.py` | **Il cervello degli indicatori.** La funzione `add_indicators()` prende un tabellone di candele (OHLCV) e aggiunge i **45 indicatori tecnici + 9 pattern candele** usando `pandas-ta` e `TA-Lib`. È usata sia quando si scaricano/ricalcolano i dati, sia dalla dashboard. È il pezzo più importante da tenere condiviso: deve calcolare gli indicatori **sempre allo stesso modo**. |
| `__init__.py` | Marker di pacchetto. Non si tocca. |

---

## 🏭 data_pipeline/ — costruzione del database (Fase 1)

Tutto ciò che riguarda **prendere i dati da Polygon e costruire il database**. Questo mondo è praticamente finito: gira ogni tanto, per aggiornare i dati.

| File | Cosa fa | Quando si usa |
|---|---|---|
| `download_history.py` | **Lo scaricatore principale.** Prende 5 anni di candele 15 min per i 66 titoli da Polygon, calcola gli indicatori, salva in DuckDB. Gestisce il rate limit e può riprendere se interrotto. Definisce anche lo **schema della tabella `candles`**. | Una volta sola (~8h). Già fatto. |
| `download_macro.py` | Scarica 4 serie macro da FRED (VIX, tasso Fed, inflazione CPI, disoccupazione) nella tabella `macro`. | Per aggiornare i dati macro. |
| `recalculate_indicators.py` | Ricalcola **tutti** gli indicatori su tutto il database. Aggiunge le colonne nuove se mancano. | Dopo aver aggiunto/modificato indicatori in `calculate.py`. |
| `build_dataset.py` | Unisce `candles` + `macro` e produce `data/processed/dataset.parquet`, con la colonna target `return_next`. | Dopo modifiche ai dati. |
| `verify_quality.py` | Controllo qualità **base**: copertura, buchi temporali, valori anomali, NaN. | Per controllare i dati. |
| `deep_check.py` | Controllo qualità **approfondito** in 8 categorie (integrità OHLC, salti sospetti, spike, prezzi congelati, ecc.). | Per controlli seri. |
| `fix_meta.py` | Pulisce META: toglie le candele prima del 2022-06-09 (quando era Facebook/"FB") e ricalcola gli indicatori. | Solo dopo aver ri-scaricato META. |
| `restore_from_parquet.py` | **Recupero d'emergenza.** Ripristina uno o più titoli nel DB partendo dal `dataset.parquet`. | Se si perdono dati nel DB. |
| `verify_connection.py` | Verifica che la API key Polygon funzioni e che lo storico sia accessibile. | Prima di scaricare. |
| `install.sh` | Crea il virtual environment e installa le librerie. | Setup iniziale su un nuovo PC. |
| `README.md` | **Guida completa della pipeline**: come scarica da Polygon, calcola gli indicatori, crea le candele, e come ricostruire il DB da zero. | Da leggere per capire la pipeline. |
| `__init__.py` | Marker di pacchetto. Non si tocca. |

---

## 📊 dashboard/ — software di visualizzazione (Mondo 2)

La dashboard interattiva (Plotly/Dash). **Legge** il database e mostra grafici a candele, indicatori, heatmap, crescita settori, schede dei singoli titoli e un glossario. Non è un unico file: è un **software modulare**, un componente per cartella. Si lancia con `python dashboard/app.py` (apre http://127.0.0.1:8050).

| File / cartella | Cosa fa |
|---|---|
| `app.py` | **L'unico file da lanciare.** Mette insieme i pezzi: crea l'app, monta le 7 tab, collega i callback. |
| `indicators/` | **Il catalogo degli indicatori** (`catalog.py`): la fonte di verità unica con nome, categoria, colonne DB, descrizione e regole di disegno di ogni indicatore. Alimenta glossario, menu e grafici. |
| `data/` | **Le query al database.** `connection.py` (connessione unica read-only), `candles.py` (candele ricalcolate + cache), `indicators.py` (indicatori memorizzati: di un titolo o di un settore), `heatmap.py` (performance), `sectors.py` (crescita settori), `stats.py` (stato DB). |
| `charts/` | **La costruzione dei grafici.** `candlestick.py`, `stock_detail.py` (pagina azione), `sector_indicator.py` (confronto per settore), `heatmap.py`, `sector_growth.py`, più `theme.py` (colori e stile condivisi). |
| `components/` | **Pezzi di interfaccia riutilizzabili**: `header.py` (intestazione), `info_card.py` (card di spiegazione), `options.py` (liste menu condivise: ticker, periodi). |
| `tabs/` | **Le 7 schermate**: `chart_tab.py` (📈 Grafico), `stock_tab.py` (🔬 Azione), `sector_indicator_tab.py` (🧭 Indicatori per settore), `heatmap_tab.py` (🟩 Heatmap), `growth_tab.py` (📊 Settori), `glossary_tab.py` (📚 Indicatori), `database_tab.py` (💾 Database). |
| `callbacks/` | **La logica interattiva**: `register.py` collega i controlli (dropdown, checkbox) ai grafici. |
| `README.md` | **Guida completa della dashboard**: architettura, tutti i grafici spiegati, come modificarla. |
| `__init__.py` | Marker di pacchetto in ogni cartella. Non si toccano. |

> Per capire come è fatta e come modificarla → [dashboard/README.md](dashboard/README.md).

---

## 🧠 training/ — le due IA (Mondo 3, Fasi 2 e 3)

Il "cervello che impara", separato dalla pipeline dati. Legge il database e usa `shared/`, ma non scarica nulla. Contiene **due IA distinte**, ognuna nella sua cartella, più i pezzi **condivisi**:

```
training/
├── config.py        (condiviso: tutti i numeri)
├── data/            (condiviso: finestre + normalizzazione)
├── occhio/          IA #1 — VEDERE / crea le forme   (FATTA, Fase 2)
└── predittore/      IA #2 — PREVEDERE su/giù         (DA FARE, Fase 3)
```

**Condivisi — usati da entrambe le IA:**
| File | Cosa fa |
|---|---|
| `config.py` | Tutti i numeri in un posto: finestra (64 candele), firma (32), dizionario (256), date di split, lista delle 47 feature. |
| `data/windows.py` | Legge il DB, **taglia la storia in finestre** da un giorno, divide train/val/test per data. |
| `data/normalize.py` | Porta forma + indicatori alla **stessa scala** (la "forma" che riceve l'occhio). |
| `README.md` | La visione d'insieme delle due IA. |

**`occhio/` — IA #1: crea le forme (FATTA, validata):**
| File | Cosa fa |
|---|---|
| `COME_FUNZIONA_LOCCHIO.md` | **Guida tecnica** dell'occhio: ogni funzione, la rete VQ-VAE, epoche, rischi/pro/miglioramenti. |
| `architecture/encoder.py` | Comprime una finestra in una firma (Conv1d). |
| `architecture/quantizer.py` | Il **dizionario** (codebook): aggancia la firma alla forma più simile tra 256. |
| `architecture/decoder.py` | **Ridisegna** la finestra dalla firma. |
| `architecture/vqvae.py` | Assembla `Autoencoder` (Passo A) e `VQVAE` (Passo B). |
| `train.py` | Il **ciclo di addestramento**. Log live in `logs/training.log`. |
| `evaluate.py` | I **3 test** di verifica (ricostruzione, mappa 2D, stabilità). |
| `pattern_memory.py` | Tira fuori e **disegna la libreria** in `models/pattern_memory/`. |
| `mostra_finestra.py` · `mostra_ricostruzione.py` | Visualizzazioni HTML (finestra→forma; originale vs copia). |

**`predittore/` — IA #2: prevede su/giù (DA FARE):**
| File | Cosa fa |
|---|---|
| `README.md` | Cosa farà la seconda IA + cosa abbiamo imparato dalla sonda. |
| `sonda_predittiva.py` | La **sonda diagnostica**: ha misurato che la forma da sola non prevede (≈50%). Log in `logs/probe.log`. |
| `train_predittore.py` | *(da creare)* il ciclo di addestramento della testa decisionale. |

> Capire l'occhio → [training/occhio/COME_FUNZIONA_LOCCHIO.md](training/occhio/COME_FUNZIONA_LOCCHIO.md) · la seconda IA → [training/predittore/README.md](training/predittore/README.md) · le roadmap → [Fase 2](Regole/Roadmap%20delle%20fasi/Fase2_Roadmap.md) e [Fase 3](Regole/Roadmap%20delle%20fasi/Fase3_Roadmap.md).

---

## 💾 data/ — i dati (pesanti, fuori da GitHub)

I file qui dentro sono troppo grandi per GitHub e sono già in `.gitignore`. Si rigenerano con gli script o si copiano a mano.

### data/raw/

| File | Cosa fa |
|---|---|
| `market.duckdb` | **Il database principale** (~1,74 GB). Contiene tutte le candele e i dati macro. Vedi sotto le 3 tabelle. Non si apre a mano: lo leggono/scrivono gli script. |
| `.gitkeep` | File vuoto che serve solo a tenere la cartella `raw/` dentro git anche quando il `.duckdb` è escluso. |

### data/processed/

| File | Cosa fa |
|---|---|
| `dataset.parquet` | **Il dataset assemblato** (~0,45 GB): candele + macro + target `return_next`. Serve anche da **backup degli OHLCV originali** (ci ha già salvati una volta recuperando AAPL e NVDA). |
| `.gitkeep` | Tiene la cartella `processed/` in git. |

### Le 3 tabelle dentro `market.duckdb`

| Tabella | Righe | Cosa contiene |
|---|---|---|
| `candles` | 3.508.585 | Una riga per candela 15 min. Colonne: `ticker`, `sector`, `ts` (data/ora), OHLCV + `vwap`, poi i **45 indicatori** e i **9 pattern candele** (56 colonne totali). |
| `macro` | 1.826 | Una riga al giorno. Colonne: `date`, `vix`, `fed_rate`, `cpi`, `unemployment`. |
| `download_log` | 66 | Una riga per titolo scaricato: `ticker`, `from_date`, `to_date`, `candles`, `downloaded_at`. Serve a sapere cosa è già stato scaricato. |

---

## 🤖 models/ — i modelli addestrati e la libreria

Prodotti dal training. I modelli pesanti (`.pt`) sono esclusi da git: si rigenerano con `train.py`.

| File | Cosa fa |
|---|---|
| `occhio_autoencoder.pt` | L'occhio del **Passo A** (solo ricopia, senza dizionario). |
| `occhio_vqvae.pt` | L'occhio del **Passo B** (col dizionario) — il modello principale dello Stadio 1. |
| `pattern_memory/codebook.npy` | Il **dizionario** salvato: le 256 forme in numeri. |
| `pattern_memory/libreria.html` | La **libreria visiva**: le forme più frequenti disegnate, da aprire nel browser. |
| `.gitkeep` | Tiene la cartella in git. |

---

## 📜 logs/ — i registri delle operazioni

File di testo con lo storico di cosa hanno fatto gli script. Utili per capire cosa è andato storto.

| File | Cosa fa |
|---|---|
| `download.log` | Log dei download singoli (per ticker). |
| `download_full.log` | Log del download completo iniziale dello storico. |
| `macro.log` | Log dello scaricamento dei dati macro FRED. |
| `training.log` | **Log dell'addestramento** (Fase 2): errore di ricopiatura per epoca e forme del dizionario usate. Si segue dal vivo con `tail -f logs/training.log`. |

---

## 📓 notebooks/ — analisi libere

Cartella per i Jupyter notebook (esperimenti, grafici, analisi al volo). Per ora vuota.

---

## 📐 Regole/ — i documenti del progetto

La "memoria" del progetto: visione, filosofia, roadmap. Da leggere per capire dove stiamo andando.

### Regole/Documento_Principale/

| File | Cosa fa |
|---|---|
| `AI-Market-Predictor-V4.docx` | Il documento di progetto originale (Word), versione 4.0 — la visione completa. |
| `README.md` | La versione Markdown e **aggiornata** del documento principale: include le decisioni della Fase 2 (VQ-VAE, memoria pattern, ritmo 15 min) e lo stato "Fase 1 completata". |
| `~$-Market-Predictor-V4.docx` | File temporaneo creato da Word quando il .docx è aperto. Ignorabile (è in `.gitignore`). |

#### Regole/Documento_Principale/Old/

Versioni vecchie del documento, tenute per storico:
| File | Cosa fa |
|---|---|
| `AI-Market-Predictor-V2.docx` | Versione 2 del documento. |
| `AI-Market-Predictor-V3.docx` | Versione 3 del documento. |
| `AI-Market-Predictor-Roadmap.docx` | Vecchia roadmap. |

### Regole/Roadmap delle fasi/

| File | Cosa fa |
|---|---|
| `AI_MarketPredictor_Fase1_Roadmap.docx` | La roadmap originale della Fase 1 (Word). |
| `README.md` | La versione Markdown e aggiornata della roadmap Fase 1, con tutti i 5 passi segnati come completati. |
| `Fase2_Roadmap.md` | **La roadmap della Fase 2**: Stadio 1 (Vedere) col VQ-VAE, la memoria dei pattern, i 6 passi concreti, e una panoramica dello Stadio 2. |
| `Fase3_Roadmap.md` | **La roadmap della Fase 3**: il predittore (Stadio 2 — Associare), cosa abbiamo imparato dalla sonda, e i passi per arrivare a >53% out-of-sample. |

---

## 📄 File alla radice del progetto

| File | Cosa fa |
|---|---|
| `README.md` | La documentazione principale: struttura, dati, schema del DB, dashboard, come si usa tutto. È il punto di partenza per chi apre il progetto. |
| `readmeIstruzioniAvvio.md` | La guida **pratica**: quali comandi lanciare per avviare la dashboard, scaricare dati, ecc. Da tenere a portata. |
| `readme_Istruzioni_cartelle.md` | **Questo file**: la mappa di cosa contiene ogni cartella e ogni file. |
| `DuckDB.session.sql` | Query SQL pronte per esplorare il database dentro VS Code (estensione SQLTools + DuckDB). |
| `.gitignore` | Dice a git cosa **non** salvare: il `.env` (segreti), `.venv/` (librerie), i file dati pesanti, i backup, le cache. |

---

## ⚙️ Cartelle di sistema (non si toccano)

Cartelle tecniche generate dagli strumenti. Non vanno modificate a mano.

| Cartella | Cosa fa |
|---|---|
| `.venv/` | Il virtual environment: tutte le librerie Python del progetto. Escluso da git (si ricrea con `install.sh`). |
| `.git/` | Gli interni del repository git (storia dei commit). Gestito da git. |
| `.claude/` | Impostazioni locali di Claude Code (`settings.local.json`). |
| `.vscode/` | Impostazioni dell'editor VS Code per questo progetto. |
| `__pycache__/` | Cache di Python (file `.pyc` compilati). Si rigenera da sola, esclusa da git. |

---

*AI Market Predictor — Fase 1 completata, Fase 2 in corso. Vedi [README.md](README.md) per i dettagli e [readmeIstruzioniAvvio.md](readmeIstruzioniAvvio.md) per i comandi.*
