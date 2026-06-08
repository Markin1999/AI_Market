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

```
ai_market_predictor/
│
├── config/                         # Configurazione globale
│   ├── .env                        # API key Polygon + FRED (NON committare)
│   ├── settings.py                 # Parametri centralizzati del progetto
│   └── __init__.py
│
├── data/
│   ├── raw/
│   │   └── market.duckdb           # Database principale (~759 MB)
│   └── processed/
│       └── dataset.parquet         # Dataset di training assemblato (~426 MB)
│
├── logs/                           # Log di download e operazioni
│
├── models/                         # Modelli RL addestrati (Fase 3 - vuoto)
│
├── notebooks/                      # Jupyter notebook per analisi (vuoto)
│
├── scripts/
│   ├── data/
│   │   ├── download_history.py     # [P2] Scarica storico Polygon.io → DuckDB (una tantum)
│   │   ├── download_macro.py       # Scarica dati macro FRED → tabella macro
│   │   ├── build_dataset.py        # Unisce candles + macro → dataset.parquet
│   │   ├── verify_quality.py       # [P3] Controllo qualità base
│   │   ├── deep_check.py           # [P3] Controllo qualità approfondito
│   │   └── fix_meta.py             # Pulizia dati META (cambio ticker FB→META)
│   │
│   ├── indicators/
│   │   └── calculate.py            # Calcola indicatori tecnici su OHLCV
│   │
│   ├── setup/
│   │   ├── install.sh              # Setup ambiente (venv + dipendenze)
│   │   └── verify_connection.py    # [P1] Verifica API key e accesso Polygon.io
│   │
│   ├── utils/                      # Funzioni condivise (da popolare)
│   │
│   └── viz/
│       └── dashboard.py            # [P4] Dashboard interattiva Plotly/Dash
│
├── Regole/
│   ├── Documento_Principale/
│   │   └── AI-Market-Predictor-V4.docx   # Documento di progetto (V4.0)
│   └── Roadmap delle fasi/
│       └── AI_MarketPredictor_Fase1_Roadmap.docx  # Roadmap Fase 1
│
├── DuckDB.session.sql              # Query SQL per esplorare il DB (SQLTools)
├── README.md
└── .gitignore                      # Esclude .env, .venv, .duckdb da git
```

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

### `config/.env`
Contiene le API key (entrambe gratuite/personali):
```
POLYGON_API_KEY=la_tua_key_polygon
FRED_API_KEY=la_tua_key_fred
```
**Non committare mai questo file su git.** È già in `.gitignore`.

### `config/settings.py`
Configurazione centralizzata — tutti gli script importano da qui invece di avere valori hardcoded:
- `POLYGON_API_KEY`, `FRED_API_KEY` — lette da `.env`
- `TICKERS_BY_SECTOR`, `ALL_TICKERS`, `TICKER_TO_SECTOR` — universo titoli
- `DB_PATH` — percorso del file DuckDB
- Parametri candele: `CANDLE_MULTIPLIER = 15`, `HISTORY_YEARS = 5`
- Parametri indicatori: `RSI_PERIOD`, `EMA_PERIODS`, `MACD_*`, `BB_*`, `ATR_PERIOD`

---

### `scripts/setup/install.sh`
Crea il virtual environment e installa le dipendenze. Da eseguire una volta sola.
```bash
bash scripts/setup/install.sh
```

### `scripts/setup/verify_connection.py`  ·  Passo 1
Verifica che la API key Polygon sia valida e che lo storico a 5 anni sia accessibile, prima di scaricare.
```bash
python scripts/setup/verify_connection.py
```

---

### `scripts/indicators/calculate.py`
Calcola gli indicatori tecnici su un DataFrame OHLCV con `pandas-ta`. Usato sia da `download_history.py` (sulle candele 15min) sia dalla dashboard (sulle candele aggregate del timeframe mostrato).

Indicatori: **RSI 14**, **MACD 12/26/9**, **EMA 20/50/200**, **Bollinger Bands 20/2**, **ATR 14**, pattern **doji** (gli altri pattern richiedono TA-Lib, ora placeholder).

### `scripts/data/download_history.py`  ·  Passo 2
**Script principale del download. Eseguito una volta sola** (~8 ore per il rate limit Polygon).

Scarica le candele 15min di 5 anni per i 66 ticker, calcola gli indicatori, salva in DuckDB. Gestisce il rate limit (5 call/min) e supporta ripresa.
```bash
python scripts/data/download_history.py            # download completo
python scripts/data/download_history.py --resume   # riprende se interrotto
python scripts/data/download_history.py --ticker AAPL
```
Crea le tabelle `candles` e `download_log`.

### `scripts/data/download_macro.py`
Scarica 4 serie macroeconomiche da **FRED API** (gratuita) e le salva nella tabella `macro`, allineate su indice giornaliero con forward-fill per i valori mensili. ~30 secondi.
```bash
python scripts/data/download_macro.py
```
Serie: **VIX** (giornaliero), **Fed Funds Rate** (giornaliero), **CPI** (mensile), **disoccupazione** (mensile).

### `scripts/data/build_dataset.py`
Unisce `candles` + `macro` per data e produce `data/processed/dataset.parquet`, pronto per il training. Aggiunge la colonna **`return_next`** = rendimento % della candela successiva (il target che il modello RL userà per imparare).
```bash
python scripts/data/build_dataset.py
```

### `scripts/data/verify_quality.py`  ·  Passo 3
Controllo qualità **base**: copertura per ticker, gaps nel time series, valori anomali (prezzi ≤0, high<low, RSI fuori range), NaN negli indicatori, verifica su periodi storici noti.
```bash
python scripts/data/verify_quality.py
```

### `scripts/data/deep_check.py`  ·  Passo 3
Controllo qualità **approfondito** in 8 categorie: integrità OHLC, salti giornalieri sospetti (split/dati sporchi), spike isolati (fat finger), prezzi congelati, coerenza indicatori, NaN dopo il warmup, sanità tabella macro, outlier di volume.
```bash
python scripts/data/deep_check.py
```
Risultato attuale: **0 problemi critici**. I salti >20% trovati sono tutti eventi reali (earnings, rally dazi 9 apr 2025, spin-off EXC).

### `scripts/data/fix_meta.py`
Pulisce i dati di META: rimuove le candele precedenti al **2022-06-09** e **ricalcola gli indicatori da zero** sulla serie pulita. Vedi sezione "Qualità dati" sotto.
```bash
python scripts/data/fix_meta.py
```

### `scripts/viz/dashboard.py`  ·  Passo 4
Dashboard interattiva. Vedi sezione "Dashboard" sotto.
```bash
python scripts/viz/dashboard.py     # poi apri http://127.0.0.1:8050
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
python scripts/viz/dashboard.py
# apri http://127.0.0.1:8050
```

Quattro tab:

- **📈 Grafico** — candlestick + volume + RSI + MACD, con EMA e Bollinger sovrapponibili. Selezioni ticker e periodo. Riquadro "ℹ️ Cosa sto guardando?" con la spiegazione di ogni indicatore.
- **🟩 Heatmap settoriale** — i 66 titoli colorati per performance sul periodo scelto.
- **📊 Settori nel tempo** — crescita % di ogni settore, ogni linea parte da 0%. Click sulla legenda per isolare un settore.
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
bash scripts/setup/install.sh

# 2. Configura le API key in config/.env
#    POLYGON_API_KEY=...   (https://polygon.io)
#    FRED_API_KEY=...      (https://fred.stlouisfed.org/docs/api/api_key.html)

# 3. Verifica connessione
python scripts/setup/verify_connection.py

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
