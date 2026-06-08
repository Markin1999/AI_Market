"""
Fase 2 — Assembla il dataset di training unendo candele + dati macro.

Per ogni candela 15min aggiunge i valori macro del giorno corrispondente
(VIX, Fed rate, CPI, disoccupazione) con forward-fill per i valori mensili.

Aggiunge anche la colonna target: rendimento % sulla candela successiva,
che il modello RL userà per capire se la mossa era giusta.

Output: data/processed/dataset.parquet
    - Una riga per candela
    - Tutte le feature già normalizzate pronte per il training
    - Colonna `return_next` = rendimento % candela successiva (target)

Uso:
    python scripts/data/build_dataset.py
    python scripts/data/build_dataset.py --ticker AAPL   # solo un ticker
"""
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
import duckdb

from config.settings import DB_PATH, ALL_TICKERS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

OUTPUT_PATH = Path(__file__).parent.parent.parent / "data" / "processed" / "dataset.parquet"


def load_candles(conn: duckdb.DuckDBPyConnection, tickers: list[str]) -> pd.DataFrame:
    placeholders = ", ".join(["?" for _ in tickers])
    df = conn.execute(f"""
        SELECT
            ticker, sector, ts,
            open, high, low, close, volume, vwap,
            rsi, macd, macd_signal, macd_hist,
            ema_20, ema_50, ema_200,
            bb_upper, bb_mid, bb_lower, atr,
            cdl_doji, cdl_hammer, cdl_engulfing,
            cdl_morning_star, cdl_evening_star
        FROM candles
        WHERE ticker IN ({placeholders})
        ORDER BY ticker, ts
    """, tickers).df()

    log.info(f"Candele caricate: {len(df):,} righe, {df['ticker'].nunique()} ticker")
    return df


def load_macro(conn: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    df = conn.execute("""
        SELECT date, vix, fed_rate, cpi, unemployment
        FROM macro
        ORDER BY date
    """).df()
    df["date"] = pd.to_datetime(df["date"])
    log.info(f"Macro caricato: {len(df):,} giorni")
    return df


def join_macro(candles: pd.DataFrame, macro: pd.DataFrame) -> pd.DataFrame:
    # Estrai la data dalla colonna ts per la join
    candles["date"] = pd.to_datetime(candles["ts"]).dt.normalize()

    # Merge con i dati macro per data
    df = candles.merge(macro, on="date", how="left")

    # Forward-fill per i giorni senza dati macro (weekend, festivi)
    for col in ["vix", "fed_rate", "cpi", "unemployment"]:
        df[col] = df[col].ffill()

    missing = df[["vix", "fed_rate", "cpi", "unemployment"]].isna().sum().sum()
    if missing > 0:
        log.warning(f"Valori macro mancanti dopo ffill: {missing} — verifica la tabella macro")

    df = df.drop(columns=["date"])
    return df


def add_target(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggiunge `return_next`: rendimento % della candela successiva per lo stesso ticker.
    Il modello RL usa questo valore per capire se la sua decisione era corretta.
    Positivo = il prezzo è salito, negativo = è sceso.
    """
    df = df.sort_values(["ticker", "ts"]).copy()
    df["return_next"] = (
        df.groupby("ticker")["close"]
        .pct_change()
        .shift(-1)  # rendimento della candela SUCCESSIVA
    )
    # L'ultima candela di ogni ticker non ha successiva — la droppiamo
    df = df.dropna(subset=["return_next"])
    return df


def print_summary(df: pd.DataFrame):
    print()
    print("=== Dataset di training ===")
    print(f"  Righe totali : {len(df):,}")
    print(f"  Ticker       : {df['ticker'].nunique()}")
    print(f"  Settori      : {df['sector'].nunique()}")
    print(f"  Periodo      : {df['ts'].min()} → {df['ts'].max()}")
    print(f"  Feature      : {len(df.columns)} colonne")
    print(f"  Dimensione   : {df.memory_usage(deep=True).sum() / 1_048_576:.1f} MB in RAM")
    print()
    print("  Campione (ultime 3 colonne aggiunte):")
    print(df[["ticker", "ts", "vix", "fed_rate", "return_next"]].tail(5).to_string(index=False))
    print()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticker", help="Processa solo questo ticker")
    args = parser.parse_args()

    tickers = [args.ticker.upper()] if args.ticker else ALL_TICKERS

    conn = duckdb.connect(str(DB_PATH))

    log.info("Carico candele dal database...")
    candles = load_candles(conn, tickers)

    log.info("Carico dati macro...")
    macro = load_macro(conn)

    conn.close()

    log.info("Join candele + macro per data...")
    df = join_macro(candles, macro)

    log.info("Calcolo rendimento target (candela successiva)...")
    df = add_target(df)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    log.info(f"Salvo dataset in {OUTPUT_PATH}...")
    df.to_parquet(OUTPUT_PATH, index=False)

    size_mb = OUTPUT_PATH.stat().st_size / 1_048_576
    log.info(f"Dataset salvato: {size_mb:.1f} MB")

    print_summary(df)


if __name__ == "__main__":
    main()
