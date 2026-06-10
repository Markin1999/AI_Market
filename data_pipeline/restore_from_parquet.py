"""
Ripristina ticker specifici nel database dal dataset.parquet originale.

Usato per recuperare AAPL e NVDA dopo che il loro storico completo (5 anni,
extended hours) era andato perso e Polygon ora serve solo 2 anni.

Il parquet contiene OHLCV originali completi → si ricaricano e si ricalcolano
TUTTI gli indicatori (inclusi i nuovi) sulla serie intera.

Uso:
    python data_pipeline/restore_from_parquet.py AAPL NVDA
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
import duckdb
from shared.indicators.calculate import add_indicators

DB_PATH = "data/raw/market.duckdb"
PARQUET = "data/processed/dataset.parquet"
RAW_COLS = "ticker, sector, ts, open, high, low, close, volume, vwap"


def main(tickers):
    conn = duckdb.connect(DB_PATH)

    col_info     = conn.execute("PRAGMA table_info('candles')").fetchall()
    db_cols      = [r[1] for r in col_info]
    int_cols     = {r[1] for r in col_info if "INT" in r[2].upper()}
    varchar_cols = {r[1] for r in col_info if "VARCHAR" in r[2].upper()}

    for ticker in tickers:
        # 1. Carica OHLCV originale dal parquet
        df = conn.execute(
            f"SELECT {RAW_COLS} FROM read_parquet('{PARQUET}') "
            f"WHERE ticker = ? ORDER BY ts", [ticker]
        ).fetchdf()

        if df.empty:
            print(f"{ticker}: NON trovato nel parquet, skip")
            continue

        first, last, n = df["ts"].min().date(), df["ts"].max().date(), len(df)
        print(f"{ticker}: dal parquet {n:,} candele ({first} → {last})")

        # 2. Ricalcola tutti gli indicatori sulla serie completa
        df = add_indicators(df)

        # 3. Allinea colonne e tipi
        for col in db_cols:
            if col not in df.columns:
                df[col] = None
        df = df[db_cols]
        for col in df.columns:
            if col in varchar_cols:
                df[col] = df[col].astype(object)
            elif col in int_cols:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype("int64")
            elif col != "ts":
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # 4. Rimpiazza nel DB
        conn.execute("DELETE FROM candles WHERE ticker = ?", [ticker])
        conn.execute("INSERT INTO candles BY NAME SELECT * FROM df")

        # 5. Aggiorna download_log
        conn.execute("""
            INSERT OR REPLACE INTO download_log (ticker, from_date, to_date, candles)
            VALUES (?, ?, ?, ?)
        """, [ticker, first.isoformat(), last.isoformat(), n])

        check = conn.execute(
            "SELECT COUNT(*) FROM candles WHERE ticker = ?", [ticker]
        ).fetchone()[0]
        print(f"{ticker}: ripristinato → {check:,} candele nel DB\n")

    conn.close()


if __name__ == "__main__":
    targets = sys.argv[1:] or ["AAPL", "NVDA"]
    main(targets)
