"""
Ricalcola tutti gli indicatori tecnici per tutte le candele del database.
Da eseguire dopo aver aggiunto nuovi indicatori a calculate.py.

Cosa fa:
  1. Aggiunge le nuove colonne al DB se non esistono
  2. Per ogni ticker: carica i dati, ricalcola, rimpiazza le righe
  3. Mostra il progresso ticker per ticker

Tempo stimato: 5-10 minuti (3.5M candele, 66 ticker).
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
import duckdb
from shared.indicators.calculate import add_indicators

DB_PATH = "data/raw/market.duckdb"

NEW_COLUMNS = {
    # Momentum
    "stoch_k":   "DOUBLE",  "stoch_d":   "DOUBLE",
    "roc":       "DOUBLE",  "williams_r": "DOUBLE", "cci": "DOUBLE",
    # Trend — direzione
    "psar_long":     "DOUBLE",  "psar_short":    "DOUBLE",
    "psar_reversal": "INTEGER",
    "aroon_up":  "DOUBLE",  "aroon_down": "DOUBLE", "aroon_osc": "DOUBLE",
    # Trend — forza
    "adx":       "DOUBLE",  "adx_plus":  "DOUBLE",  "adx_minus": "DOUBLE",
    # Volatilità — canali
    "dc_upper":  "DOUBLE",  "dc_lower":  "DOUBLE",
    "kc_upper":  "DOUBLE",  "kc_lower":  "DOUBLE",
    # Volume
    "obv":         "DOUBLE", "mfi":         "DOUBLE",
    "cmf":         "DOUBLE", "force_index": "DOUBLE",
    # Ichimoku
    "ichi_tenkan": "DOUBLE", "ichi_kijun":  "DOUBLE",
    "ichi_span_a": "DOUBLE", "ichi_span_b": "DOUBLE", "ichi_chikou": "DOUBLE",
    # Pattern candele nuovi
    "cdl_shooting_star":   "INTEGER", "cdl_hanging_man":     "INTEGER",
    "cdl_harami":          "INTEGER", "cdl_inverted_hammer": "INTEGER",
}

RAW_COLS = "ticker, sector, ts, open, high, low, close, volume, vwap"


def main():
    t0 = time.time()
    conn = duckdb.connect(DB_PATH)

    # 1. Aggiungi nuove colonne se mancano
    existing = {r[1] for r in conn.execute("PRAGMA table_info('candles')").fetchall()}
    added = []
    for col, dtype in NEW_COLUMNS.items():
        if col not in existing:
            conn.execute(f"ALTER TABLE candles ADD COLUMN {col} {dtype}")
            added.append(col)
    if added:
        print(f"Aggiunte {len(added)} colonne: {', '.join(added)}\n")
    else:
        print("Colonne già presenti — aggiorno i valori.\n")

    # 2. Ordine e tipi colonne nel DB
    col_info    = conn.execute("PRAGMA table_info('candles')").fetchall()
    db_cols     = [r[1] for r in col_info]
    int_cols    = {r[1] for r in col_info if "INT" in r[2].upper()}
    varchar_cols= {r[1] for r in col_info if "VARCHAR" in r[2].upper()}

    # 3. Lista ticker
    tickers = [r[0] for r in conn.execute(
        "SELECT DISTINCT ticker FROM candles ORDER BY ticker"
    ).fetchall()]
    total = len(tickers)
    print(f"Ricalcolo indicatori per {total} ticker...\n")

    for i, ticker in enumerate(tickers, 1):
        t1 = time.time()

        df = conn.execute(
            f"SELECT {RAW_COLS} FROM candles WHERE ticker = ? ORDER BY ts", [ticker]
        ).fetchdf()

        if df.empty:
            print(f"  [{i:02d}/{total}] {ticker}: nessuna candela, skip")
            continue

        df = add_indicators(df)

        # Assicura che tutte le colonne DB siano presenti
        for col in db_cols:
            if col not in df.columns:
                df[col] = None

        df = df[db_cols]

        # Normalizza tipi per DuckDB (None/object → float64 o int64)
        for col in df.columns:
            if col in varchar_cols:
                df[col] = df[col].astype(object)
            elif col in int_cols:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype("int64")
            elif col != "ts":
                df[col] = pd.to_numeric(df[col], errors="coerce")

        conn.execute("DELETE FROM candles WHERE ticker = ?", [ticker])
        conn.execute("INSERT INTO candles BY NAME SELECT * FROM df")

        elapsed = time.time() - t1
        print(f"  [{i:02d}/{total}] {ticker:6s}  {len(df):>7,} candele  ({elapsed:.1f}s)")

    total_time = time.time() - t0
    print(f"\nRicalcolo completato in {total_time/60:.1f} minuti.")
    print(f"Colonne totali per candela: {len(db_cols)}")
    conn.close()


if __name__ == "__main__":
    main()
