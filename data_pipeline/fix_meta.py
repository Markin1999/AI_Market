"""
Fix dati META — rimuove le candele precedenti al 9 giugno 2022.

Prima di quella data il ticker "META" apparteneva a un'altra azienda
(Facebook ha cambiato ticker da FB a META il 2022-06-09). I prezzi ~$15
del 2021/inizio 2022 non sono di Meta Platforms e vanno rimossi.

Gli indicatori delle candele rimanenti vengono ricalcolati da zero,
perché quelli originali erano stati calcolati usando i prezzi sbagliati.

Uso:
    python data_pipeline/fix_meta.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import duckdb
import pandas as pd

from shared.config.settings import DB_PATH
from shared.indicators.calculate import add_indicators
from data_pipeline.download_history import CANDLE_COLUMNS, _INT_COLS

CUTOFF = "2022-06-09"


def main():
    conn = duckdb.connect(str(DB_PATH))  # read-write

    # Stato prima
    before = conn.execute("SELECT COUNT(*) FROM candles WHERE ticker='META'").fetchone()[0]
    bad = conn.execute(
        "SELECT COUNT(*) FROM candles WHERE ticker='META' AND ts < ?", [CUTOFF]
    ).fetchone()[0]
    print(f"META candele totali ora:        {before:,}")
    print(f"META candele sporche (< {CUTOFF}): {bad:,}")

    # 1. Leggi OHLCV puliti (dal cutoff in poi)
    df = conn.execute("""
        SELECT ticker, sector, ts, open, high, low, close, volume, vwap
        FROM candles
        WHERE ticker='META' AND ts >= ?
        ORDER BY ts
    """, [CUTOFF]).df()
    print(f"META candele pulite da tenere:  {len(df):,}")

    # 2. Ricalcola indicatori da zero sulla serie pulita
    print("Ricalcolo indicatori sulla serie pulita...")
    df = add_indicators(df)

    # 3. Cancella TUTTE le righe META
    conn.execute("DELETE FROM candles WHERE ticker='META'")

    # 4. Allinea colonne e tipi, poi reinserisci
    for col in CANDLE_COLUMNS:
        if col not in df.columns:
            df[col] = 0 if col in _INT_COLS else float("nan")
    df = df[CANDLE_COLUMNS].copy()
    df["ticker"] = df["ticker"].astype(object)
    df["sector"] = df["sector"].astype(object)
    df["ts"] = df["ts"].astype("datetime64[ns]")
    for col in _INT_COLS:
        df[col] = df[col].fillna(0).astype("int64")
    for col in CANDLE_COLUMNS:
        if col not in _INT_COLS and col not in ("ticker", "sector", "ts"):
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("float64")

    conn.execute("INSERT INTO candles SELECT * FROM df")

    # 5. Aggiorna download_log
    conn.execute("""
        UPDATE download_log SET from_date=?, candles=? WHERE ticker='META'
    """, [df["ts"].min().date().isoformat(), len(df)])

    # Verifica finale
    after = conn.execute("SELECT COUNT(*) FROM candles WHERE ticker='META'").fetchone()[0]
    rng = conn.execute(
        "SELECT MIN(ts)::DATE, MAX(ts)::DATE, MIN(close), MAX(close) FROM candles WHERE ticker='META'"
    ).fetchone()

    print()
    print(f"✓ META ripulito: {before:,} → {after:,} candele")
    print(f"  Periodo: {rng[0]} → {rng[1]}")
    print(f"  Prezzo close: min={rng[2]:.2f}  max={rng[3]:.2f}")

    total = conn.execute("SELECT COUNT(*) FROM candles").fetchone()[0]
    print(f"  Candele totali nel DB: {total:,}")
    conn.close()


if __name__ == "__main__":
    main()
