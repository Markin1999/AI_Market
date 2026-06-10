# Data Pipeline — Come funziona e come ricostruire il database

Questa cartella contiene tutto ciò che trasforma i dati grezzi di Polygon.io in un database pronto per il training del modello.

---

## Il flusso completo

```
Polygon.io API          FRED API
     │                      │
     ▼                      ▼
download_history.py    download_macro.py
     │                      │
     │  candele OHLCV        │  VIX, Fed rate, CPI, disoccupazione
     │  + 45 indicatori      │
     ▼                      ▼
         market.duckdb
         ┌──────────────┐
         │  candles     │  3.5M righe, 56 colonne
         │  macro       │  1.826 righe, 5 colonne
         │  download_log│  66 righe (una per ticker)
         └──────────────┘
                │
                ▼
         build_dataset.py
                │  join candele + macro per data
                │  aggiunge colonna target (return_next)
                ▼
         dataset.parquet  (~0.45 GB)
```

---

## Passo 1 — Download storico candele (`download_history.py`)

**Cosa fa:** Chiama l'API Polygon.io e scarica 5 anni di candele a 15 minuti per tutti i 66 ticker. Per ogni ticker: scarica → calcola indicatori → salva nel DB.

**Quanto ci vuole:** ~8 ore (rate limit Polygon: 5 chiamate/minuto, 12s di pausa tra le batch).

**Struttura di una candela:**

| Campo | Tipo | Descrizione |
|---|---|---|
| `ticker` | VARCHAR | Es. "AAPL" |
| `sector` | VARCHAR | Es. "Technology" |
| `ts` | TIMESTAMP | Data e ora della candela (UTC, senza fuso) |
| `open` | DOUBLE | Prezzo di apertura |
| `high` | DOUBLE | Massimo |
| `low` | DOUBLE | Minimo |
| `close` | DOUBLE | Prezzo di chiusura |
| `volume` | DOUBLE | Volumi scambiati |
| `vwap` | DOUBLE | Volume Weighted Average Price |
| + 47 colonne | — | Indicatori tecnici e pattern (vedi sezione dedicata) |

**Come richiama Polygon:** La chiamata è paginata — ogni pagina ha al massimo 50.000 risultati. Se ci sono più pagine, `next_url` viene restituito nella risposta e lo script lo segue automaticamente finché non finisce. La serie viene scaricata in ordine cronologico (`sort=asc`).

**Rate limit:** `CALL_DELAY_SEC = 12s` tra ogni chiamata. Se arriva un `429 Too Many Requests`, lo script aspetta 60 secondi e riprova.

**Modalità resume:** Con `--resume` salta i ticker già presenti in `download_log`. Utile se il download si interrompe a metà.

```bash
python data_pipeline/download_history.py              # tutti i 66 ticker (~8h)
python data_pipeline/download_history.py --ticker AAPL  # solo AAPL (~5 min)
python data_pipeline/download_history.py --resume       # riprendi da dove eri
```

> ⚠️ **Polygon Starter serve solo ~2 anni di storico.** Il DB attuale contiene 5 anni (scaricati quando il piano lo permetteva). Non ri-scaricare ticker che hanno già i 5 anni — perderesti 3 anni di dati irrecuperabili.

---

## Passo 2 — Calcolo indicatori tecnici (`shared/indicators/calculate.py`)

Chiamato automaticamente da `download_history.py` su ogni ticker. Prende un DataFrame OHLCV e restituisce lo stesso DataFrame con 45 indicatori + 9 pattern candele aggiunti come nuove colonne.

**Librerie:** `pandas-ta` (0.4.71b0) per la maggior parte degli indicatori, `TA-Lib` (0.6.8) per i pattern candele.

### I 45 indicatori

**Momentum (6 indicatori)**

| Colonna | Formula | Cosa misura |
|---|---|---|
| `rsi` | RSI(14) | Forza relativa del movimento. > 70 = ipercomprato, < 30 = ipervenduto |
| `stoch_k` | Stocastico K(14,3,3) | Posizione del close rispetto al range recente (0–100) |
| `stoch_d` | Media mobile di stoch_k | Segnale più lento dello stocastico |
| `roc` | Rate of Change(10) | Variazione % rispetto a 10 candele fa |
| `williams_r` | Williams %R(14) | Simile allo stocastico ma invertito (0 = top, -100 = bottom) |
| `cci` | CCI(14) | Deviazione dal prezzo "tipico" medio. > +100 forte trend, < -100 trend inverso |

**Trend — direzione (11 indicatori)**

| Colonna | Formula | Cosa misura |
|---|---|---|
| `macd` | MACD(12,26,9) | Differenza tra EMA veloce e lenta |
| `macd_signal` | EMA(9) del MACD | Linea di segnale del MACD |
| `macd_hist` | MACD − signal | Forza e direzione del momentum |
| `ema_20` | EMA(20) | Media mobile esponenziale breve |
| `ema_50` | EMA(50) | Media mobile esponenziale media |
| `ema_200` | EMA(200) | Media mobile esponenziale lunga (trend principale) |
| `psar_long` | PSAR(0.02, 0.2) | Parabolic SAR in trend rialzista (support) |
| `psar_short` | PSAR(0.02, 0.2) | Parabolic SAR in trend ribassista (resistance) |
| `psar_reversal` | 0/1 | 1 = il PSAR ha appena invertito direzione |
| `aroon_up` | Aroon(25) up | Quante candele fa era il massimo degli ultimi 25 periodi |
| `aroon_down` | Aroon(25) down | Quante candele fa era il minimo degli ultimi 25 periodi |
| `aroon_osc` | aroon_up − aroon_down | Positivo = trend up, negativo = trend down |

**Trend — forza (3 indicatori)**

| Colonna | Formula | Cosa misura |
|---|---|---|
| `adx` | ADX(14) | Forza del trend (0–100). > 25 = trend forte, < 20 = laterale |
| `adx_plus` | DI+(14) | Pressione rialzista |
| `adx_minus` | DI−(14) | Pressione ribassista |

**Volatilità (8 indicatori)**

| Colonna | Formula | Cosa misura |
|---|---|---|
| `bb_upper` | Bollinger Upper(20, 2σ) | Banda superiore — potenziale resistenza |
| `bb_mid` | Bollinger Mid(20) | Media mobile centrale delle Bollinger |
| `bb_lower` | Bollinger Lower(20, 2σ) | Banda inferiore — potenziale supporto |
| `atr` | ATR(14) | Average True Range: volatilità assoluta in punti prezzo |
| `dc_upper` | Donchian Upper(20) | Massimo degli ultimi 20 periodi |
| `dc_lower` | Donchian Lower(20) | Minimo degli ultimi 20 periodi |
| `kc_upper` | Keltner Upper(20, 2) | Banda superiore basata su ATR |
| `kc_lower` | Keltner Lower(20, 2) | Banda inferiore basata su ATR |

**Volume (4 indicatori)**

| Colonna | Formula | Cosa misura |
|---|---|---|
| `obv` | On-Balance Volume | Volume cumulativo: sale se il close > open, scende altrimenti |
| `mfi` | Money Flow Index(14) | RSI del "flusso di denaro" (include i volumi). 0–100 |
| `cmf` | Chaikin Money Flow(20) | Flusso netto di denaro rispetto al volume totale. Da -1 a +1 |
| `force_index` | Force Index(13) | Prezzo × volume: misura la "forza" dietro ogni candela |

**Ichimoku (5 indicatori)**

| Colonna | Formula | Cosa misura |
|---|---|---|
| `ichi_tenkan` | (max9 + min9) / 2 | Linea di conversione — trend a breve |
| `ichi_kijun` | (max26 + min26) / 2 | Linea base — trend a medio |
| `ichi_span_a` | (tenkan + kijun) / 2, spostato avanti 26 | Bordo superiore della "nuvola" |
| `ichi_span_b` | (max52 + min52) / 2, spostato avanti 26 | Bordo inferiore della "nuvola" |
| `ichi_chikou` | Close spostato indietro 26 | Linea lagging: conferma o contraddice il trend |

### I 9 pattern candele (via TA-Lib)

Ogni colonna vale `100` (segnale rialzista), `-100` (segnale ribassista), o `0` (pattern assente).

| Colonna | Pattern | Segnale tipico |
|---|---|---|
| `cdl_doji` | Doji | Indecisione — possibile inversione |
| `cdl_hammer` | Hammer | Inversione rialzista (dopo discesa) |
| `cdl_engulfing` | Engulfing | Inversione: la candela corrente "ingoia" la precedente |
| `cdl_morning_star` | Morning Star | Inversione rialzista a 3 candele |
| `cdl_evening_star` | Evening Star | Inversione ribassista a 3 candele |
| `cdl_shooting_star` | Shooting Star | Inversione ribassista (dopo salita) |
| `cdl_hanging_man` | Hanging Man | Possibile inversione ribassista (dopo salita) |
| `cdl_harami` | Harami | Inversione: candela piccola contenuta in quella precedente |
| `cdl_inverted_hammer` | Inverted Hammer | Inversione rialzista (dopo discesa) |

**Nota sul warmup:** I primi N valori di ogni indicatore sono `NaN` perché non ci sono abbastanza candele precedenti. Es: EMA(200) ha 199 valori NaN all'inizio di ogni ticker. È normale e atteso.

---

## Passo 3 — Download dati macro (`download_macro.py`)

**Cosa fa:** Scarica 4 serie macroeconomiche da FRED (gratuita) nella tabella `macro`.

| Serie FRED | Colonna DB | Frequenza | Cosa rappresenta |
|---|---|---|---|
| VIXCLS | `vix` | giornaliera | CBOE Volatility Index — "paura del mercato" |
| DFF | `fed_rate` | giornaliera | Federal Funds Rate effettivo |
| CPIAUCSL | `cpi` | mensile | Consumer Price Index (inflazione) |
| UNRATE | `unemployment` | mensile | Tasso di disoccupazione USA |

I valori mensili (CPI, UNRATE) vengono estesi a tutti i giorni con **forward-fill**: l'ultimo valore mensile noto viene ripetuto fino al mese successivo.

```bash
python data_pipeline/download_macro.py
```

---

## Passo 4 — Assemblare il dataset (`build_dataset.py`)

**Cosa fa:** Unisce candele + macro in un unico file Parquet pronto per il training.

**Come funziona la join:** Le candele hanno timestamp a 15 minuti, i macro hanno granularità giornaliera. La join avviene estraendo la data dal timestamp (senza ora) e cercando il valore macro per quel giorno. Weekend e festivi usano il valore del giorno lavorativo precedente (forward-fill).

**Colonna target `return_next`:** Rendimento percentuale della candela successiva per lo stesso ticker:
```
return_next[i] = (close[i+1] - close[i]) / close[i]
```
Il modello RL usa questo valore per capire se la decisione presa sulla candela `i` era giusta. L'ultima candela di ogni ticker non ha successiva e viene scartata.

```bash
python data_pipeline/build_dataset.py
python data_pipeline/build_dataset.py --ticker AAPL  # solo AAPL
```

Output: `data/processed/dataset.parquet` (~0.45 GB).

> **Doppia funzione del parquet:** Oltre ad essere il dataset di training, il file contiene gli OHLCV originali e serve da **backup di emergenza**. Se i dati nel DB vengono corrotti o cancellati, `restore_from_parquet.py` li recupera da qui.

---

## Come ricostruire il database da zero

Se il database è perso o corrotto, questi sono i passi nell'ordine giusto:

```bash
# 0. Prerequisiti (solo la prima volta su un nuovo computer)
brew install ta-lib
bash data_pipeline/install.sh
source .venv/bin/activate
pip install dash-bootstrap-components pyarrow TA-Lib

# 1. Verifica che le API key funzionino
python data_pipeline/verify_connection.py

# 2. Scarica lo storico (~8 ore — prendi un caffè)
python data_pipeline/download_history.py

# 3. Scarica i dati macro (< 1 minuto)
python data_pipeline/download_macro.py

# 4. Pulizia META (indispensabile — ha dati pre-rebrand sporchi)
python data_pipeline/fix_meta.py

# 5. Controlla la qualità
python data_pipeline/verify_quality.py
python data_pipeline/deep_check.py

# 6. Assembla il dataset di training
python data_pipeline/build_dataset.py
```

> ⚠️ Polygon ora serve solo ~2 anni di storico. Il database attuale ha 5 anni. Se perdi il DB e lo riscarichi, avrai solo 2 anni per tutti i ticker tranne AAPL e NVDA (recuperabili dal parquet con `restore_from_parquet.py`).

---

## Operazioni di manutenzione

### Aggiungere/modificare un indicatore

1. Modifica `shared/indicators/calculate.py`
2. Aggiungi la colonna a `CANDLE_COLUMNS` e `_INT_COLS` (se integer) in `download_history.py`
3. Aggiungi la colonna allo schema `CREATE TABLE` in `init_db()` — o usa `ALTER TABLE` se il DB esiste già
4. Ricalcola tutto:
```bash
python data_pipeline/recalculate_indicators.py
```

### Recupero d'emergenza di un ticker

Se un ticker è stato cancellato per sbaglio dal DB ma esiste nel parquet:
```bash
python data_pipeline/restore_from_parquet.py AAPL NVDA
```
Lo script ricarica gli OHLCV originali dal parquet, ricalcola tutti gli indicatori, e reinserisce nel DB.

### Aggiornare solo META dopo un re-download

META ha un problema speciale: prima del 9 giugno 2022 il ticker "META" apparteneva a un'altra azienda (Facebook usava "FB"). Se riscarichi META, i dati pre-2022 sono spazzatura.
```bash
python data_pipeline/download_history.py --ticker META
python data_pipeline/fix_meta.py
```

---

## Stato attuale del database

| Tabella | Righe | Periodo |
|---|---|---|
| `candles` | 3.508.585 | ~2021 → 2026 (5 anni, 66 ticker) |
| `macro` | 1.826 | 2021 → 2026 |
| `download_log` | 66 | Una riga per ticker |

Dimensione su disco: `market.duckdb` ~1.74 GB · `dataset.parquet` ~0.45 GB

---

*Per i comandi operativi → [readmeIstruzioniAvvio.md](../readmeIstruzioniAvvio.md) · Per la mappa di tutte le cartelle → [readme_Istruzioni_cartelle.md](../readme_Istruzioni_cartelle.md)*
