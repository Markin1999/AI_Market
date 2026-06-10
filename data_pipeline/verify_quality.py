"""
Passo 3 — Verifica qualità dei dati storici nel database.

Controlla:
  1. Copertura per ticker (candele totali, date min/max)
  2. Gaps nel time series (sessioni di mercato mancanti)
  3. Valori anomali (prezzi negativi, volumi zero, RSI fuori range)
  4. NaN negli indicatori (normale nelle prime candele, anomalo nel mezzo)
  5. Confronto spot su un periodo storico noto (es. picco VIX ottobre 2022)
  6. Riepilogo finale — il database è affidabile?

Uso:
    python data_pipeline/verify_quality.py
    python data_pipeline/verify_quality.py --ticker AAPL
"""
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import duckdb
import pandas as pd

from shared.config.settings import DB_PATH, ALL_TICKERS, TICKERS_BY_SECTOR

MARKET_OPEN  = "09:30"
MARKET_CLOSE = "16:00"

# Candele attese per sessione di mercato completa (09:30-15:45, ogni 15min = 26 candele)
CANDLES_PER_SESSION = 26

SEPARATOR = "─" * 60


def section(title: str):
    print(f"\n{SEPARATOR}")
    print(f"  {title}")
    print(SEPARATOR)


def check_coverage(conn: duckdb.DuckDBPyConnection, tickers: list[str]) -> dict:
    """Candele per ticker, date min/max, verifica che siano tutti presenti."""
    section("1. COPERTURA PER TICKER")

    rows = conn.execute(f"""
        SELECT
            ticker,
            sector,
            COUNT(*)           AS candele,
            MIN(ts)::DATE      AS dal,
            MAX(ts)::DATE      AS al,
            COUNT(DISTINCT ts::DATE) AS giorni_distinti
        FROM candles
        WHERE ticker IN ({','.join(['?' for _ in tickers])})
        GROUP BY ticker, sector
        ORDER BY sector, ticker
    """, tickers).fetchall()

    coverage = {}
    missing = [t for t in tickers if t not in [r[0] for r in rows]]

    print(f"\n  {'Ticker':<8} {'Settore':<25} {'Candele':>9} {'Dal':<12} {'Al':<12} {'Giorni':>7}")
    print(f"  {'─'*8} {'─'*25} {'─'*9} {'─'*12} {'─'*12} {'─'*7}")

    current_sector = None
    for ticker, sector, candele, dal, al, giorni in rows:
        if sector != current_sector:
            current_sector = sector
            print()
        ok = "✓" if candele > 50_000 else "!"
        print(f"  {ok} {ticker:<7} {sector:<25} {candele:>9,} {str(dal):<12} {str(al):<12} {giorni:>7,}")
        coverage[ticker] = {"candele": candele, "dal": dal, "al": al, "giorni": giorni}

    if missing:
        print(f"\n  ✗ Ticker mancanti nel DB: {', '.join(missing)}")
    else:
        print(f"\n  ✓ Tutti i {len(tickers)} ticker presenti")

    total = sum(v["candele"] for v in coverage.values())
    print(f"\n  Totale candele: {total:,}")

    return coverage


def check_gaps(conn: duckdb.DuckDBPyConnection, sample_tickers: list[str]) -> int:
    """Cerca sessioni di mercato con meno candele del previsto su un campione."""
    section("2. GAPS NEL TIME SERIES (campione 5 ticker)")

    total_gaps = 0
    sample = sample_tickers[:5]

    for ticker in sample:
        rows = conn.execute("""
            SELECT
                ts::DATE AS giorno,
                COUNT(*) AS candele
            FROM candles
            WHERE ticker = ?
              AND EXTRACT(DOW FROM ts) BETWEEN 1 AND 5
            GROUP BY giorno
            HAVING COUNT(*) < ?
            ORDER BY giorno
            LIMIT 10
        """, [ticker, CANDLES_PER_SESSION - 5]).fetchall()

        if rows:
            print(f"\n  {ticker}: {len(rows)} sessioni incomplete (mostra prime 10)")
            for giorno, n in rows:
                print(f"    {giorno}  →  {n} candele (attese ~{CANDLES_PER_SESSION})")
            total_gaps += len(rows)
        else:
            print(f"  ✓ {ticker}: nessun gap rilevante")

    return total_gaps


def check_anomalies(conn: duckdb.DuckDBPyConnection, tickers: list[str]) -> int:
    """Controlla prezzi negativi, volumi zero, RSI fuori range."""
    section("3. VALORI ANOMALI")

    issues = 0

    # Prezzi negativi o zero
    r = conn.execute(f"""
        SELECT COUNT(*) FROM candles
        WHERE ticker IN ({','.join(['?' for _ in tickers])})
          AND (open <= 0 OR high <= 0 OR low <= 0 OR close <= 0)
    """, tickers).fetchone()[0]
    status = "✓" if r == 0 else f"✗ PROBLEMA"
    print(f"\n  Prezzi <= 0:          {status}  ({r} righe)")
    issues += r

    # High < Low (impossibile)
    r = conn.execute(f"""
        SELECT COUNT(*) FROM candles
        WHERE ticker IN ({','.join(['?' for _ in tickers])})
          AND high < low
    """, tickers).fetchone()[0]
    status = "✓" if r == 0 else f"✗ PROBLEMA"
    print(f"  High < Low:           {status}  ({r} righe)")
    issues += r

    # Volume zero (sospetto ma non impossibile)
    r = conn.execute(f"""
        SELECT COUNT(*) FROM candles
        WHERE ticker IN ({','.join(['?' for _ in tickers])})
          AND volume = 0
    """, tickers).fetchone()[0]
    status = "✓" if r < 100 else "!"
    print(f"  Volume = 0:           {status}  ({r} righe)")

    # RSI fuori range 0-100
    r = conn.execute(f"""
        SELECT COUNT(*) FROM candles
        WHERE ticker IN ({','.join(['?' for _ in tickers])})
          AND rsi IS NOT NULL
          AND (rsi < 0 OR rsi > 100)
    """, tickers).fetchone()[0]
    status = "✓" if r == 0 else f"✗ PROBLEMA"
    print(f"  RSI fuori [0,100]:    {status}  ({r} righe)")
    issues += r

    # Duplicati
    r = conn.execute(f"""
        SELECT COUNT(*) FROM (
            SELECT ticker, ts, COUNT(*) AS n
            FROM candles
            WHERE ticker IN ({','.join(['?' for _ in tickers])})
            GROUP BY ticker, ts
            HAVING COUNT(*) > 1
        )
    """, tickers).fetchone()[0]
    status = "✓" if r == 0 else f"✗ PROBLEMA"
    print(f"  Duplicati (ticker,ts):{status}  ({r} righe)")
    issues += r

    return issues


def check_nan_indicators(conn: duckdb.DuckDBPyConnection, tickers: list[str]):
    """Quanti NaN ci sono in ogni indicatore — normale nelle prime candele."""
    section("4. NaN NEGLI INDICATORI")

    indicators = ["rsi", "macd", "ema_20", "ema_50", "ema_200", "bb_upper", "atr"]

    print(f"\n  {'Indicatore':<15} {'NaN':>10} {'% sul totale':>14}  Note")
    print(f"  {'─'*15} {'─'*10} {'─'*14}  {'─'*30}")

    total = conn.execute(f"""
        SELECT COUNT(*) FROM candles
        WHERE ticker IN ({','.join(['?' for _ in tickers])})
    """, tickers).fetchone()[0]

    for ind in indicators:
        n = conn.execute(f"""
            SELECT COUNT(*) FROM candles
            WHERE ticker IN ({','.join(['?' for _ in tickers])})
              AND {ind} IS NULL
        """, tickers).fetchone()[0]

        pct = (n / total * 100) if total > 0 else 0
        # NaN attesi per EMA200: ~200 candele per ticker = ~13.200 su 66 ticker
        expected_ok = pct < 1.0
        status = "✓" if expected_ok else "!"
        print(f"  {status} {ind:<14} {n:>10,} {pct:>13.2f}%")


def check_spot_period(conn: duckdb.DuckDBPyConnection):
    """Verifica su periodi storici noti: crisi SVB marzo 2023, picco tassi 2023."""
    section("5. VERIFICA PERIODI STORICI NOTI")

    # Marzo 2023: crollo SVB — JPM dovrebbe avere alta volatilità
    print("\n  Marzo 2023 (crollo SVB) — JPM:")
    rows = conn.execute("""
        SELECT ts::DATE AS giorno, ROUND(MIN(low),2) AS minimo, ROUND(MAX(high),2) AS massimo,
               ROUND(AVG(volume),0) AS vol_medio
        FROM candles
        WHERE ticker = 'JPM'
          AND ts::DATE BETWEEN '2023-03-09' AND '2023-03-15'
        GROUP BY giorno
        ORDER BY giorno
    """).fetchall()

    if rows:
        for giorno, minimo, massimo, vol in rows:
            print(f"    {giorno}  low={minimo}  high={massimo}  vol={int(vol):,}")
    else:
        print("    ! Nessun dato trovato per questo periodo")

    # Ottobre 2022: picco VIX ~34, AAPL vicino ai minimi
    print("\n  Ottobre 2022 (minimo mercato) — AAPL close:")
    rows = conn.execute("""
        SELECT ts::DATE AS giorno, ROUND(MIN(close),2) AS close_min, ROUND(AVG(rsi),1) AS rsi_medio
        FROM candles
        WHERE ticker = 'AAPL'
          AND ts::DATE BETWEEN '2022-10-10' AND '2022-10-14'
        GROUP BY giorno
        ORDER BY giorno
    """).fetchall()

    if rows:
        for giorno, close_min, rsi in rows:
            print(f"    {giorno}  close_min={close_min}  rsi_medio={rsi}")
    else:
        print("    ! Nessun dato trovato per questo periodo")


def print_final_verdict(issues: int, gaps: int, coverage: dict, tickers: list[str]):
    section("VERDETTO FINALE")

    all_tickers_present = len(coverage) == len(tickers)
    enough_candles = all(v["candele"] > 50_000 for v in coverage.values())
    no_anomalies = issues == 0
    few_gaps = gaps < 50

    checks = [
        ("Tutti i ticker presenti",         all_tickers_present),
        ("Candele sufficienti per ticker",   enough_candles),
        ("Nessun valore anomalo",            no_anomalies),
        ("Gaps minimi nel time series",      few_gaps),
    ]

    all_ok = all(ok for _, ok in checks)

    print()
    for label, ok in checks:
        icon = "✓" if ok else "✗"
        print(f"  {icon}  {label}")

    print()
    if all_ok:
        print("  ✅  DATABASE AFFIDABILE — si può procedere con il Passo 4 (dashboard)")
    else:
        print("  ⚠️  Ci sono problemi da risolvere prima di procedere")
    print()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticker", help="Verifica solo questo ticker")
    args = parser.parse_args()

    tickers = [args.ticker.upper()] if args.ticker else ALL_TICKERS

    print(f"\n{'═'*60}")
    print(f"  AI MARKET PREDICTOR — Verifica qualità dati")
    print(f"  Database: {DB_PATH}")
    print(f"  Ticker: {len(tickers)}")
    print(f"{'═'*60}")

    conn = duckdb.connect(str(DB_PATH), read_only=True)

    coverage = check_coverage(conn, tickers)
    gaps     = check_gaps(conn, tickers)
    issues   = check_anomalies(conn, tickers)
    check_nan_indicators(conn, tickers)
    check_spot_period(conn)
    print_final_verdict(issues, gaps, coverage, tickers)

    conn.close()


if __name__ == "__main__":
    main()
