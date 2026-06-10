"""
Passo 2 — Scarica lo storico completo (6 anni, 15 min) per tutti i 66 ticker
e calcola gli indicatori tecnici su ogni candela.
Salva tutto in DuckDB — operazione da fare una volta sola.

Uso:
    python data_pipeline/download_history.py
    python data_pipeline/download_history.py --ticker AAPL   # solo un ticker
    python data_pipeline/download_history.py --resume        # continua download interrotto
"""
import sys
import time
import argparse
import logging
from pathlib import Path
from datetime import datetime, timedelta, date

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import requests
import pandas as pd
import duckdb

from shared.config.settings import (
    POLYGON_API_KEY, ALL_TICKERS, TICKER_TO_SECTOR,
    CANDLE_MULTIPLIER, HISTORY_YEARS, DB_PATH,
)
from shared.indicators.calculate import add_indicators

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/download.log"),
    ],
)
log = logging.getLogger(__name__)

BASE_URL = "https://api.polygon.io"
# Polygon Starter: max 50.000 risultati per chiamata, max 5 call/min sul piano base
RESULTS_PER_CALL = 50_000
CALL_DELAY_SEC = 12   # 5 call/min = 1 ogni 12s (con margine di sicurezza)


def init_db(conn: duckdb.DuckDBPyConnection):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS candles (
            ticker       VARCHAR NOT NULL,
            sector       VARCHAR NOT NULL,
            ts           TIMESTAMP NOT NULL,
            open         DOUBLE,
            high         DOUBLE,
            low          DOUBLE,
            close        DOUBLE,
            volume       DOUBLE,
            vwap         DOUBLE,
            -- Indicatori tecnici
            rsi          DOUBLE,
            macd         DOUBLE,
            macd_signal  DOUBLE,
            macd_hist    DOUBLE,
            ema_20       DOUBLE,
            ema_50       DOUBLE,
            ema_200      DOUBLE,
            bb_upper     DOUBLE,
            bb_mid       DOUBLE,
            bb_lower     DOUBLE,
            atr          DOUBLE,
            -- Momentum
            stoch_k    DOUBLE, stoch_d    DOUBLE,
            roc        DOUBLE, williams_r DOUBLE, cci DOUBLE,
            -- Trend — direzione
            psar_long    DOUBLE, psar_short    DOUBLE, psar_reversal INTEGER,
            aroon_up     DOUBLE, aroon_down    DOUBLE, aroon_osc     DOUBLE,
            -- Trend — forza
            adx        DOUBLE, adx_plus  DOUBLE, adx_minus DOUBLE,
            -- Volatilità — canali
            dc_upper   DOUBLE, dc_lower  DOUBLE,
            kc_upper   DOUBLE, kc_lower  DOUBLE,
            -- Volume
            obv          DOUBLE, mfi          DOUBLE,
            cmf          DOUBLE, force_index  DOUBLE,
            -- Ichimoku
            ichi_tenkan DOUBLE, ichi_kijun  DOUBLE,
            ichi_span_a DOUBLE, ichi_span_b DOUBLE, ichi_chikou DOUBLE,
            -- Pattern candele (100=rialzista, -100=ribassista, 0=assente)
            cdl_hammer          INTEGER, cdl_engulfing       INTEGER,
            cdl_doji            INTEGER, cdl_morning_star    INTEGER,
            cdl_evening_star    INTEGER, cdl_shooting_star   INTEGER,
            cdl_hanging_man     INTEGER, cdl_harami          INTEGER,
            cdl_inverted_hammer INTEGER,
            PRIMARY KEY (ticker, ts)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS download_log (
            ticker      VARCHAR NOT NULL,
            from_date   DATE NOT NULL,
            to_date     DATE NOT NULL,
            candles     INTEGER,
            downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (ticker)
        )
    """)


def already_downloaded(conn: duckdb.DuckDBPyConnection, ticker: str) -> bool:
    result = conn.execute(
        "SELECT COUNT(*) FROM download_log WHERE ticker = ?", [ticker]
    ).fetchone()
    return result[0] > 0


def fetch_candles(ticker: str, from_date: str, to_date: str) -> list[dict]:
    """Scarica tutte le candele 15min per un ticker in un range di date."""
    url = (
        f"{BASE_URL}/v2/aggs/ticker/{ticker}/range/"
        f"{CANDLE_MULTIPLIER}/minute/{from_date}/{to_date}"
    )
    all_results = []
    params = {
        "apiKey": POLYGON_API_KEY,
        "adjusted": "true",
        "sort": "asc",
        "limit": RESULTS_PER_CALL,
    }

    while True:
        resp = requests.get(url, params=params, timeout=30)
        if resp.status_code == 429:
            log.warning("Rate limit raggiunto — attendo 60s...")
            time.sleep(60)
            continue
        if resp.status_code != 200:
            log.error(f"{ticker}: HTTP {resp.status_code} — {resp.text[:200]}")
            break

        data = resp.json()
        results = data.get("results", [])
        all_results.extend(results)

        next_url = data.get("next_url")
        if not next_url:
            break
        url = next_url
        params = {"apiKey": POLYGON_API_KEY}
        time.sleep(CALL_DELAY_SEC)

    return all_results


def results_to_dataframe(ticker: str, results: list[dict]) -> pd.DataFrame:
    if not results:
        return pd.DataFrame()

    df = pd.DataFrame(results)
    df = df.rename(columns={
        "t": "ts", "o": "open", "h": "high",
        "l": "low", "c": "close", "v": "volume", "vw": "vwap",
    })
    df["ts"] = pd.to_datetime(df["ts"], unit="ms", utc=True).dt.tz_localize(None)
    df["ticker"] = ticker
    df["sector"] = TICKER_TO_SECTOR.get(ticker, "Unknown")

    cols = ["ticker", "sector", "ts", "open", "high", "low", "close", "volume", "vwap"]
    df = df[[c for c in cols if c in df.columns]]

    # Ordina e rimuovi duplicati
    df = df.sort_values("ts").drop_duplicates(subset=["ts"])
    return df


CANDLE_COLUMNS = [
    "ticker", "sector", "ts", "open", "high", "low", "close", "volume", "vwap",
    "rsi", "macd", "macd_signal", "macd_hist",
    "ema_20", "ema_50", "ema_200",
    "bb_upper", "bb_mid", "bb_lower", "atr",
    # Momentum
    "stoch_k", "stoch_d", "roc", "williams_r", "cci",
    # Trend — direzione
    "psar_long", "psar_short", "psar_reversal",
    "aroon_up", "aroon_down", "aroon_osc",
    # Trend — forza
    "adx", "adx_plus", "adx_minus",
    # Volatilità — canali
    "dc_upper", "dc_lower", "kc_upper", "kc_lower",
    # Volume
    "obv", "mfi", "cmf", "force_index",
    # Ichimoku
    "ichi_tenkan", "ichi_kijun", "ichi_span_a", "ichi_span_b", "ichi_chikou",
    # Pattern candele
    "cdl_hammer", "cdl_engulfing", "cdl_doji", "cdl_morning_star", "cdl_evening_star",
    "cdl_shooting_star", "cdl_hanging_man", "cdl_harami", "cdl_inverted_hammer",
]
# Colonne integer — default 0
_INT_COLS = {
    "cdl_hammer", "cdl_engulfing", "cdl_doji", "cdl_morning_star", "cdl_evening_star",
    "cdl_shooting_star", "cdl_hanging_man", "cdl_harami", "cdl_inverted_hammer",
    "psar_reversal",
}


def save_to_db(conn: duckdb.DuckDBPyConnection, df: pd.DataFrame, ticker: str):
    if df.empty:
        return

    # Allinea colonne e tipi alla definizione della tabella candles
    for col in CANDLE_COLUMNS:
        if col not in df.columns:
            df[col] = 0 if col in _INT_COLS else float("nan")

    df = df[CANDLE_COLUMNS].copy()

    # pandas 3.x usa StringDtype e datetime64[ms] — DuckDB 0.10 vuole object e datetime64[ns]
    df["ticker"] = df["ticker"].astype(object)
    df["sector"] = df["sector"].astype(object)
    df["ts"] = df["ts"].astype("datetime64[ns]")

    for col in _INT_COLS:
        df[col] = df[col].fillna(0).astype("int64")
    for col in CANDLE_COLUMNS:
        if col not in _INT_COLS and col not in ("ticker", "sector", "ts"):
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("float64")

    conn.execute("""
        INSERT OR IGNORE INTO candles BY NAME
        SELECT * FROM df
    """)
    conn.execute("""
        INSERT OR REPLACE INTO download_log (ticker, from_date, to_date, candles)
        VALUES (?, ?, ?, ?)
    """, [
        ticker,
        df["ts"].min().date().isoformat(),
        df["ts"].max().date().isoformat(),
        len(df),
    ])


def process_ticker(conn: duckdb.DuckDBPyConnection, ticker: str, resume: bool):
    if resume and already_downloaded(conn, ticker):
        log.info(f"{ticker}: già scaricato, salto")
        return

    end_date = date.today()
    start_date = end_date - timedelta(days=365 * HISTORY_YEARS)

    log.info(f"{ticker}: scarico {start_date} → {end_date}")
    results = fetch_candles(ticker, start_date.isoformat(), end_date.isoformat())

    if not results:
        log.warning(f"{ticker}: nessun risultato")
        return

    df = results_to_dataframe(ticker, results)
    log.info(f"{ticker}: {len(df)} candele grezzo — calcolo indicatori...")
    df = add_indicators(df)
    save_to_db(conn, df, ticker)
    log.info(f"{ticker}: salvate {len(df)} candele nel database")
    time.sleep(CALL_DELAY_SEC)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticker", help="Scarica solo questo ticker")
    parser.add_argument("--resume", action="store_true", help="Salta ticker già scaricati")
    args = parser.parse_args()

    if not POLYGON_API_KEY or POLYGON_API_KEY == "inserisci_qui_la_tua_key":
        print("✗ API key non configurata in shared/config/.env")
        sys.exit(1)

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    Path("logs").mkdir(exist_ok=True)

    conn = duckdb.connect(str(DB_PATH))
    init_db(conn)

    tickers = [args.ticker.upper()] if args.ticker else ALL_TICKERS
    total = len(tickers)

    log.info(f"=== Download storico: {total} ticker ===")
    for i, ticker in enumerate(tickers, 1):
        log.info(f"[{i}/{total}] {ticker}")
        try:
            process_ticker(conn, ticker, resume=args.resume)
        except Exception as e:
            log.error(f"{ticker}: errore — {e}")

    count = conn.execute("SELECT COUNT(*) FROM candles").fetchone()[0]
    log.info(f"=== Download completato — {count:,} candele totali nel database ===")
    conn.close()


if __name__ == "__main__":
    main()
