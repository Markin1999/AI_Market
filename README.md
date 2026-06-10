# AI Market Predictor

Sistema di trading algoritmico basato su Reinforcement Learning (RL) per i mercati USA. Il modello viene addestrato su 5 anni di dati storici a 15 minuti su 66 ticker dell'S&P500 e opera senza regole hardcoded: scopre da solo i pattern attraverso il ciclo osserva → agisce → ricompensa.

> Filosofia: il sistema non viene programmato, viene *fatto crescere* come un bambino. Il mercato è il maestro, la ricompensa è l'unica guida. Vedi il documento principale in [Regole/Documento_Principale/](Regole/Documento_Principale/).

---

## Stato del progetto

**Fase 1 — Fondamenta (COMPLETATA)** — tutto gira in locale sul Mac.

| Passo | Stato | Descrizione |
|---|---|---|
| 1 — Preparare l'ambiente | ✅ | venv, dipendenze, API key Polygon.io |
| 2 — Scaricare lo storico | ✅ | 3.508.587 candele, 66 ticker, 5 anni |
| 3 — Verificare la qualità | ✅ | controlli base + approfonditi, 0 problemi critici |
| 4 — Dashboard | ✅ | grafici interattivi con timeframe adattivo |
| 5 — Validare Fase 1 | ✅ | dati completi, puliti, visualizzati |

**Extra già pronti per la Fase 2 (preparazione al training):** dati macro FRED scaricati e dataset di training assemblato.

---

## Struttura del progetto

Il progetto è diviso in **due mondi separati** (pipeline dati e addestramento) che condividono un **core comune** e gli **artefatti dati**.

```
ai_market_predictor/
│
├── shared/                         # CORE CONDIVISO (usato da entrambi i mondi)
│   ├── config/
│   │   ├── .env                    # API key Polygon + FRED (NON committare)
│   │   ├── settings.py             # Parametri centralizzati (titoli, path, indicatori)
│   │   └── __init__.py
│   └── indicators/
│       └── calculate.py            # Calcola indicatori tecnici su OHLCV (UNA copia)
│
├── data_pipeline/                  # MONDO 1 — costruzione del database (Fase 1)
│   ├── download_history.py         # [P2] Scarica storico Polygon.io → DuckDB (una tantum)
│   ├── download_macro.py           # Scarica dati macro FRED → tabella macro
│   ├── build_dataset.py            # Unisce candles + macro → dataset.parquet
│   ├── recalculate_indicators.py   # Ricalcola tutti gli indicatori sul DB
│   ├── verify_quality.py           # [P3] Controllo qualità base
│   ├── deep_check.py               # [P3] Controllo qualità approfondito
│   ├── fix_meta.py                 # Pulizia dati META (cambio ticker FB→META)
│   ├── restore_from_parquet.py     # Ripristino ticker dal parquet (emergenza)
│   ├── verify_connection.py        # [P1] Verifica API key e accesso Polygon.io
│   └── install.sh                  # Setup ambiente (venv + dipendenze)
│
├── dashboard/                      # MONDO 2 — software di visualizzazione (Plotly/Dash)
│   ├── app.py                      # Entry point: python dashboard/app.py
│   ├── indicators/                 # Catalogo indicatori (fonte unica: descrizioni + colonne)
│   ├── data/                       # Query al database (candele, indicatori, heatmap, settori)
│   ├── charts/                     # Un file per tipo di grafico + tema
│   ├── components/                 # Pezzi di interfaccia riutilizzabili
│   ├── tabs/                       # Le 7 schermate
│   └── callbacks/                  # Logica interattiva (controlli → grafici)
│
├── training/                       # MONDO 3 — addestramento RL (Fase 2)
│   └── README.md                   # Legge il DB, usa shared/ — in costruzione
│
├── data/                           # ARTEFATTI DATI (pesanti, fuori da git)
│   ├── raw/
│   │   └── market.duckdb           # Database principale (~1.6 GB)
│   └── processed/
│       └── dataset.parquet         # Dataset assemblato (~447 MB, anche backup OHLCV)
│
├── models/                         # Modelli RL addestrati + memoria pattern (Fase 2)
├── logs/                           # Log di download e operazioni
├── notebooks/                      # Jupyter notebook per analisi
│
├── Regole/
│   ├── Documento_Principale/       # Documento di progetto V4.0 (.docx + README.md)
│   └── Roadmap delle fasi/         # Roadmap Fase 1 e Fase 2
│
├── DuckDB.session.sql              # Query SQL per esplorare il DB (SQLTools)
├── README.md
├── readmeIstruzioniAvvio.md        # Guida pratica di avvio
└── .gitignore                      # Esclude .env, .venv, .duckdb da git
```

> **Perché questa divisione?** La pipeline dati e l'addestramento sono lavori diversi, con dipendenze diverse. Ma il calcolo degli indicatori e la lista dei titoli **devono** restare identici tra i due (altrimenti il modello in produzione vedrebbe numeri diversi da quelli su cui ha imparato): per questo stanno in `shared/`, in una copia sola.

---

## Risultato dati (Fase 1)

- **3.508.587 candele** da 15 minuti
- **66 ticker** su 11 settori S&P500
- Copertura: **giugno 2021 → giugno 2026** (5 anni)
- **1.826 giorni** di dati macroeconomici (VIX, Fed rate, CPI, disoccupazione)
- Database DuckDB: ~759 MB · Dataset training: ~426 MB

### Ticker per settore (66 totali)

| Settore | Ticker |
|---|---|
| Technology | AAPL, MSFT, NVDA, AMD, GOOGL, META |
| Financials | JPM, BAC, GS, MS, BRK.B, C |
| Health Care | JNJ, UNH, PFE, ABBV, MRK, LLY |
| Consumer Discretionary | AMZN, TSLA, HD, MCD, NKE, SBUX |
| Consumer Staples | PG, KO, PEP, WMT, COST, CL |
| Energy | XOM, CVX, COP, SLB, EOG, PSX |
| Industrials | CAT, BA, HON, UPS, GE, LMT |
| Materials | LIN, APD, NEM, FCX, ECL, VMC |
| Real Estate | AMT, PLD, CCI, EQIX, SPG, DLR |
| Utilities | NEE, DUK, SO, AEP, EXC, XEL |
| Communication Services | NFLX, DIS, CMCSA, T, CHTR, VZ |

---

## Descrizione file per file

### `shared/config/.env`
Contiene le API key (entrambe gratuite/personali):
```
POLYGON_API_KEY=la_tua_key_polygon
FRED_API_KEY=la_tua_key_fred
```
**Non committare mai questo file su git.** È già in `.gitignore`.

### `shared/config/settings.py`
Configurazione centralizzata — tutti gli script importano da qui invece di avere valori hardcoded:
- `POLYGON_API_KEY`, `FRED_API_KEY` — lette da `.env`
- `TICKERS_BY_SECTOR`, `ALL_TICKERS`, `TICKER_TO_SECTOR` — universo titoli
- `DB_PATH`, `PARQUET_PATH` — percorsi degli artefatti dati
- Parametri candele: `CANDLE_MULTIPLIER = 15`, `HISTORY_YEARS = 5`
- Parametri indicatori: `RSI_PERIOD`, `EMA_PERIODS`, `MACD_*`, `BB_*`, `ATR_PERIOD`

### `shared/indicators/calculate.py`
Calcola gli indicatori tecnici su un DataFrame OHLCV con `pandas-ta` + `TA-Lib`. Usato sia da `download_history.py`/`recalculate_indicators.py` (sulle candele 15min) sia dalla dashboard (sulle candele aggregate del timeframe mostrato).

**45 indicatori** in 6 categorie: momentum (RSI, Stocastico, ROC, Williams %R, CCI), trend-direzione (MACD, EMA 20/50/200, Parabolic SAR, Aroon), trend-forza (ADX +DI/−DI), volatilità (Bollinger, ATR, Donchian, Keltner), volume (OBV, MFI, CMF, Force Index), Ichimoku, + **9 pattern candele** (doji, hammer, engulfing, morning/evening star, shooting star, hanging man, harami, inverted hammer).

---

### `data_pipeline/install.sh`
Crea il virtual environment e installa le dipendenze. Da eseguire una volta sola.
```bash
bash data_pipeline/install.sh
```

### `data_pipeline/verify_connection.py`  ·  Passo 1
Verifica che la API key Polygon sia valida e che lo storico sia accessibile, prima di scaricare.
```bash
python data_pipeline/verify_connection.py
```

### `data_pipeline/download_history.py`  ·  Passo 2
**Script principale del download. Eseguito una volta sola** (~8 ore per il rate limit Polygon).

Scarica le candele 15min di 5 anni per i 66 ticker, calcola gli indicatori, salva in DuckDB. Gestisce il rate limit (5 call/min) e supporta ripresa.
```bash
python data_pipeline/download_history.py            # download completo
python data_pipeline/download_history.py --resume   # riprende se interrotto
python data_pipeline/download_history.py --ticker AAPL
```
Crea le tabelle `candles` e `download_log`.

> ⚠️ Il piano Polygon Starter ora serve solo ~2 anni di storico. I 5 anni nel DB sono insostituibili: **non** ri-scaricare ticker già completi.

### `data_pipeline/download_macro.py`
Scarica 4 serie macroeconomiche da **FRED API** (gratuita) e le salva nella tabella `macro`, allineate su indice giornaliero con forward-fill per i valori mensili. ~30 secondi.
```bash
python data_pipeline/download_macro.py
```
Serie: **VIX** (giornaliero), **Fed Funds Rate** (giornaliero), **CPI** (mensile), **disoccupazione** (mensile).

### `data_pipeline/recalculate_indicators.py`
Ricalcola **tutti** gli indicatori per tutte le candele del database, da eseguire dopo aver aggiunto/modificato indicatori in `calculate.py`. Aggiunge le colonne mancanti e riscrive ticker per ticker. ~1-2 minuti.
```bash
python data_pipeline/recalculate_indicators.py
```

### `data_pipeline/build_dataset.py`
Unisce `candles` + `macro` per data e produce `data/processed/dataset.parquet`. Aggiunge la colonna **`return_next`** = rendimento % della candela successiva (target per il modello RL).
```bash
python data_pipeline/build_dataset.py
```

### `data_pipeline/verify_quality.py`  ·  Passo 3
Controllo qualità **base**: copertura per ticker, gaps nel time series, valori anomali (prezzi ≤0, high<low, RSI fuori range), NaN negli indicatori, verifica su periodi storici noti.
```bash
python data_pipeline/verify_quality.py
```

### `data_pipeline/deep_check.py`  ·  Passo 3
Controllo qualità **approfondito** in 8 categorie: integrità OHLC, salti giornalieri sospetti, spike isolati, prezzi congelati, coerenza indicatori, NaN dopo il warmup, sanità tabella macro, outlier di volume.
```bash
python data_pipeline/deep_check.py
```
Risultato attuale: **0 problemi critici**. I salti >20% trovati sono tutti eventi reali (earnings, rally dazi 9 apr 2025, spin-off EXC).

### `data_pipeline/fix_meta.py`
Pulisce i dati di META: rimuove le candele precedenti al **2022-06-09** e **ricalcola gli indicatori da zero** sulla serie pulita. Vedi sezione "Qualità dati" sotto.
```bash
python data_pipeline/fix_meta.py
```

### `data_pipeline/restore_from_parquet.py`
Ripristina uno o più ticker nel database a partire da `dataset.parquet` (rete di sicurezza se i dati nel DB vengono persi). Ricalcola gli indicatori sulla serie recuperata.
```bash
python data_pipeline/restore_from_parquet.py AAPL NVDA
```

### `dashboard/app.py`  ·  Software di visualizzazione
Dashboard interattiva modulare. Vedi sezione "Dashboard" sotto e [dashboard/README.md](dashboard/README.md) per l'architettura.
```bash
python dashboard/app.py     # poi apri http://127.0.0.1:8050
```

---

## Database `data/raw/market.duckdb`

**Non si tocca a mano — scritto e letto dagli script.**

### Tabella `candles` (una riga per candela 15min)

| Colonna | Tipo | Descrizione |
|---|---|---|
| ticker, sector | VARCHAR | Simbolo e settore |
| ts | TIMESTAMP | Data/ora candela (UTC, no timezone) |
| open, high, low, close | DOUBLE | Prezzi OHLC |
| volume | DOUBLE | Volume scambiato |
| vwap | DOUBLE | Volume Weighted Average Price |
| rsi | DOUBLE | RSI 14 |
| macd, macd_signal, macd_hist | DOUBLE | MACD 12/26/9 |
| ema_20, ema_50, ema_200 | DOUBLE | Medie mobili esponenziali |
| bb_upper, bb_mid, bb_lower | DOUBLE | Bollinger Bands |
| atr | DOUBLE | Average True Range 14 |
| cdl_hammer, cdl_engulfing, cdl_doji, cdl_morning_star, cdl_evening_star | INTEGER | Pattern candele (1/0/-1) |

### Tabella `macro` (una riga per giorno)

| Colonna | Tipo | Descrizione |
|---|---|---|
| date | DATE | Data |
| vix | DOUBLE | CBOE Volatility Index |
| fed_rate | DOUBLE | Federal Funds Rate (%) |
| cpi | DOUBLE | Consumer Price Index (inflazione) |
| unemployment | DOUBLE | Tasso di disoccupazione (%) |

### Tabella `download_log`
Traccia per ogni ticker il range di date scaricato e il numero di candele.

---

## Dataset `data/processed/dataset.parquet`

Il file pronto per il training: ogni riga è una candela con OHLCV + indicatori + contesto macro del giorno + `return_next`. 30 colonne, ~3,5M righe. Lo legge il modello RL durante l'addestramento (Fase 3). Si rigenera con `build_dataset.py` ogni volta che cambiano i dati nel DB.

---

## Qualità dati — nota importante su META

Guardando il grafico "Settori nel tempo" è emerso che META mostrava una crescita impossibile (+3795%). Causa: **Facebook ha tradato come "FB" fino al 9 giugno 2022**, poi ha adottato il ticker META. Prima di quella data, "META" apparteneva a un'altra azienda (~$15). Polygon.io restituisce sotto "META" anche lo storico del precedente proprietario.

**Fix applicato** (`fix_meta.py`): rimosse le 6.613 candele precedenti al 2022-06-09 e ricalcolati gli indicatori. META ora ha ~4 anni di storia pulita (dal 2022-06-09). Polygon Starter non dà i dati di Facebook sotto "FB", quindi quell'anno è irrecuperabile.

⚠️ **Se ri-scarichi META, va ripulito di nuovo** con `fix_meta.py`, poi rigenera `dataset.parquet`. È l'unico ticker dei 66 con questo problema (verificato con `deep_check.py`).

Altra caratteristica nota (non un bug): lo **spin-off di Constellation Energy da EXC** (feb 2022) crea un −25% che non fu una perdita reale per chi deteneva le azioni.

---

## Dashboard

```bash
python dashboard/app.py
# apri http://127.0.0.1:8050
```
Software modulare (un componente per cartella) — architettura in [dashboard/README.md](dashboard/README.md).

Sette tab:

- **📈 Grafico** — candlestick + volume + RSI + MACD, con EMA e Bollinger sovrapponibili. Selezioni ticker e periodo. Riquadro "ℹ️ Cosa sto guardando?" con la spiegazione di ogni indicatore.
- **🔬 Azione** — scheda completa di un titolo con *tutti* gli indicatori del DB, componibili (overlay sul prezzo, oscillatori in pannelli, pattern come frecce).
- **🧭 Indicatori per settore** — lo stesso indicatore confrontato tra tutti i titoli di un settore.
- **🟩 Heatmap settoriale** — i 66 titoli colorati per performance sul periodo scelto.
- **📊 Settori nel tempo** — crescita % di ogni settore, ogni linea parte da 0%. Click sulla legenda per isolare un settore.
- **📚 Indicatori** — glossario: ogni indicatore spiegato (cos'è, come si legge), generato dal catalogo.
- **💾 Database** — candele e copertura per ogni ticker.

**Timeframe adattivo (performance):** la dashboard aggrega le candele in base al periodo, così disegna sempre poche centinaia di punti invece di milioni. Gli indicatori si ricalcolano sul timeframe mostrato.

| Periodo | Candele |
|---|---|
| 1 settimana | 15 minuti |
| 1 mese | 1 ora |
| 3 mesi | 4 ore |
| 6 mesi – 2 anni | giornaliere |
| 5 anni | settimanali |

---

## Polygon.io vs cosa calcoliamo noi

**Polygon.io fornisce solo dati grezzi:** `open, high, low, close, volume, vwap, timestamp`.
**Noi calcoliamo tutti gli indicatori** (RSI, MACD, EMA, Bollinger, ATR, pattern) prima di salvarli. Il modello RL usa gli indicatori come *features* di input, non i prezzi grezzi.

---

## Setup iniziale (per nuovi ambienti)

```bash
# 1. Crea venv e installa dipendenze
bash data_pipeline/install.sh

# 2. Configura le API key in shared/config/.env
#    POLYGON_API_KEY=...   (https://polygon.io)
#    FRED_API_KEY=...      (https://fred.stlouisfed.org/docs/api/api_key.html)

# 3. Verifica connessione
python data_pipeline/verify_connection.py

# 4. Il DB storico è già in data/raw/market.duckdb — non riscaricare
```

---

## Dipendenze principali

| Libreria | Uso |
|---|---|
| `duckdb` | Database locale colonnare, query veloci su milioni di righe |
| `pandas` | Manipolazione dati |
| `pandas-ta` | Indicatori tecnici (RSI, MACD, EMA, BB, ATR) |
| `requests` | Chiamate HTTP a Polygon.io e FRED |
| `plotly` / `dash` / `dash-bootstrap-components` | Dashboard interattiva |
| `pyarrow` | Lettura/scrittura file `.parquet` |
| `python-dotenv` | Lettura variabili da `.env` |

---

## Prossimi passi (Fase 2 — Training)

1. Definire il meccanismo di **ricompensa** osservando i dati reali (decisione delicata, da non anticipare)
2. Costruire l'ambiente RL e addestrare il modello sui **4 stadi** (Vedere → Associare → Contestualizzare → Sentire)
3. Validazione out-of-sample con le 4 metriche obbligatorie (accuracy >53%, Sharpe >1.0, drawdown <20%, batte Buy&Hold)
4. Paper trading 6 mesi prima di qualsiasi soldo reale

Dettagli completi nel documento principale in [Regole/Documento_Principale/](Regole/Documento_Principale/).
