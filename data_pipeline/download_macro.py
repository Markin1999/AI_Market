"""
Fase 2 — Scarica dati macroeconomici da FRED API (gratuita) e li salva
nella tabella `macro` del database DuckDB.

Serie scaricate:
  VIXCLS   — CBOE Volatility Index (VIX), giornaliero
  DFF      — Fed Funds Rate effettivo, giornaliero
  CPIAUCSL — Consumer Price Index (inflazione), mensile
  UNRATE   — Tasso di disoccupazione USA, mensile

I dati macro vengono poi uniti alle candele in build_dataset.py al momento
del training. La join avviene per data (non per timestamp) con forward-fill
per i valori mensili.

Uso:
    python data_pipeline/download_macro.py
"""
import sys
import logging
from pathlib import Path
from datetime import date, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import requests
import pandas as pd
import duckdb

from shared.config.settings import FRED_API_KEY, DB_PATH, HISTORY_YEARS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/macro.log"),
    ],
)
log = logging.getLogger(__name__)

FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"

# Serie FRED da scaricare: id → (nome leggibile, frequenza)
FRED_SERIES = {
    "VIXCLS":   ("vix",           "daily"),
    "DFF":      ("fed_rate",      "daily"),
    "CPIAUCSL": ("cpi",           "monthly"),
    "UNRATE":   ("unemployment",  "monthly"),
}


def init_macro_table(conn: duckdb.DuckDBPyConnection):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS macro (
            date         DATE    NOT NULL PRIMARY KEY,
            vix          DOUBLE,   -- CBOE Volatility Index
            fed_rate     DOUBLE,   -- Federal Funds Rate (%)
            cpi          DOUBLE,   -- Consumer Price Index
            unemployment DOUBLE    -- Tasso disoccupazione (%)
        )
    """)
    log.info("Tabella macro pronta")


def fetch_fred_series(series_id: str, start_date: str, end_date: str) -> pd.Series:
    """Scarica una serie FRED e restituisce una pd.Series indicizzata per data."""
    params = {
        "series_id":         series_id,
        "api_key":           FRED_API_KEY,
        "file_type":         "json",
        "observation_start": start_date,
        "observation_end":   end_date,
    }
    resp = requests.get(FRED_BASE, params=params, timeout=30)

    if resp.status_code != 200:
        log.error(f"{series_id}: HTTP {resp.status_code} — {resp.text[:200]}")
        return pd.Series(dtype=float)

    data = resp.json()
    observations = data.get("observations", [])
    if not observations:
        log.warning(f"{series_id}: nessun dato ricevuto")
        return pd.Series(dtype=float)

    df = pd.DataFrame(observations)[["date", "value"]]
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["value"]).set_index("date")["value"]

    log.info(f"{series_id}: {len(df)} osservazioni ({df.index.min().date()} → {df.index.max().date()})")
    return df


def build_macro_dataframe(start_date: str, end_date: str) -> pd.DataFrame:
    """
    Scarica tutte le serie FRED e le allinea su un indice giornaliero continuo.
    I valori mensili (CPI, UNRATE) vengono propagati in avanti (forward-fill)
    per riempire i giorni intermedi.
    """
    # Indice giornaliero completo
    idx = pd.date_range(start=start_date, end=end_date, freq="D")
    macro = pd.DataFrame(index=idx)

    for series_id, (col_name, _) in FRED_SERIES.items():
        log.info(f"Scarico {series_id} ({col_name})...")
        series = fetch_fred_series(series_id, start_date, end_date)
        if series.empty:
            macro[col_name] = float("nan")
            continue
        # Allinea all'indice giornaliero e propaga in avanti i valori mensili
        macro[col_name] = series.reindex(idx).ffill()

    macro.index.name = "date"
    macro = macro.reset_index()
    macro["date"] = macro["date"].dt.date  # converte a Python date per DuckDB

    # Rimuovi righe dove TUTTI i valori macro sono NaN (weekend/festivi iniziali)
    value_cols = list(FRED_SERIES[s][0] for s in FRED_SERIES)
    macro = macro.dropna(subset=value_cols, how="all")

    return macro


def save_macro_to_db(conn: duckdb.DuckDBPyConnection, df: pd.DataFrame):
    count_before = conn.execute("SELECT COUNT(*) FROM macro").fetchone()[0]

    conn.execute("""
        INSERT OR REPLACE INTO macro (date, vix, fed_rate, cpi, unemployment)
        SELECT date, vix, fed_rate, cpi, unemployment FROM df
    """)

    count_after = conn.execute("SELECT COUNT(*) FROM macro").fetchone()[0]
    log.info(f"Macro salvate: {count_after - count_before} nuove righe (totale: {count_after})")


def print_summary(conn: duckdb.DuckDBPyConnection):
    rows = conn.execute("""
        SELECT
            MIN(date)                                    AS dal,
            MAX(date)                                    AS al,
            COUNT(*)                                     AS giorni,
            ROUND(AVG(vix), 2)                           AS vix_medio,
            ROUND(MIN(vix), 2)                           AS vix_min,
            ROUND(MAX(vix), 2)                           AS vix_max,
            ROUND(AVG(fed_rate), 3)                      AS fed_medio,
            ROUND(AVG(unemployment), 2)                  AS disoc_media
        FROM macro
    """).fetchone()

    print()
    print("=== Dati macro nel database ===")
    print(f"  Periodo      : {rows[0]} → {rows[1]}")
    print(f"  Giorni totali: {rows[2]}")
    print(f"  VIX medio    : {rows[3]}  (min {rows[4]}, max {rows[5]})")
    print(f"  Fed rate medio: {rows[6]}%")
    print(f"  Disoccupazione media: {rows[7]}%")
    print()


def main():
    if not FRED_API_KEY or FRED_API_KEY == "inserisci_qui_la_tua_key":
        print()
        print("✗ FRED API key non configurata.")
        print()
        print("  1. Vai su https://fred.stlouisfed.org/docs/api/api_key.html")
        print("  2. Registrati (gratuito) e copia la tua API key")
        print("  3. Aprì shared/config/.env e inserisci:")
        print("     FRED_API_KEY=la_tua_key_qui")
        print()
        sys.exit(1)

    end_date   = date.today().isoformat()
    start_date = (date.today() - timedelta(days=365 * HISTORY_YEARS)).isoformat()

    log.info(f"=== Download macro FRED: {start_date} → {end_date} ===")

    Path("logs").mkdir(exist_ok=True)
    conn = duckdb.connect(str(DB_PATH))
    init_macro_table(conn)

    macro_df = build_macro_dataframe(start_date, end_date)
    log.info(f"DataFrame macro costruito: {len(macro_df)} righe")

    save_macro_to_db(conn, macro_df)
    print_summary(conn)

    conn.close()
    log.info("=== Download macro completato ===")


if __name__ == "__main__":
    main()
