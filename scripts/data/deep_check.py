"""
Controllo qualità APPROFONDITO del database.
Cerca problemi sottili che la verifica base non rileva.

Controlli:
  A. Integrità OHLC (high >= open/close/low, low <= open/close)
  B. Salti giornalieri sospetti (split non aggiustati o dati sporchi)
  C. Candele anomale isolate (fat finger: spike che subito rientra)
  D. Prezzi congelati (molte candele identiche di fila con volume > 0)
  E. Coerenza indicatori (BB ordinate, ATR >= 0, RSI in range)
  F. NaN negli indicatori a metà serie (dopo il warmup — anomalo)
  G. Tabella macro (NaN, valori fuori range plausibile)
  H. Outlier di volume per ticker

Uso:
    python scripts/data/deep_check.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import duckdb

from config.settings import DB_PATH

SEP = "─" * 64
issues = {"critici": 0, "da_guardare": 0}


def section(t):
    print(f"\n{SEP}\n  {t}\n{SEP}")


def crit(n):
    issues["critici"] += n


def warn(n):
    issues["da_guardare"] += n


def main():
    conn = duckdb.connect(str(DB_PATH), read_only=True)

    # ── A. Integrità OHLC ────────────────────────────────────
    section("A. INTEGRITÀ OHLC (high/low coerenti con open/close)")
    r = conn.execute("""
        SELECT COUNT(*) FROM candles
        WHERE high < open - 0.001 OR high < close - 0.001
           OR low  > open + 0.001 OR low  > close + 0.001
           OR high < low - 0.001
    """).fetchone()[0]
    print(f"\n  Candele con OHLC impossibile: {r}")
    if r:
        crit(r)
        rows = conn.execute("""
            SELECT ticker, ts, open, high, low, close FROM candles
            WHERE high < open - 0.001 OR high < close - 0.001
               OR low  > open + 0.001 OR low  > close + 0.001
            ORDER BY ticker, ts LIMIT 10
        """).fetchall()
        for x in rows:
            print(f"    {x[0]:<6} {x[1]}  O={x[2]} H={x[3]} L={x[4]} C={x[5]}")
    else:
        print("  ✓ Tutte le candele hanno OHLC coerente")

    # ── B. Salti giornalieri sospetti ────────────────────────
    section("B. SALTI GIORNALIERI (possibili split non aggiustati / dati sporchi)")
    rows = conn.execute("""
        WITH daily AS (
            SELECT ticker, date, close FROM (
                SELECT ts::DATE AS date, ticker, close,
                       ROW_NUMBER() OVER (PARTITION BY ticker, ts::DATE ORDER BY ts DESC) AS rn
                FROM candles
            ) WHERE rn = 1
        ),
        jumps AS (
            SELECT ticker, date, close,
                   LAG(close) OVER (PARTITION BY ticker ORDER BY date) AS prev_close
            FROM daily
        )
        SELECT ticker, date, prev_close, close,
               ROUND((close - prev_close) / prev_close * 100, 1) AS pct
        FROM jumps
        WHERE prev_close IS NOT NULL
          AND ABS((close - prev_close) / prev_close) > 0.20
        ORDER BY ABS((close - prev_close) / prev_close) DESC
        LIMIT 30
    """).fetchall()
    if rows:
        print(f"\n  Salti giornalieri > 20% trovati: {len(rows)} (mostro i maggiori)")
        print(f"\n  {'Ticker':<7} {'Data':<12} {'da':>9} {'a':>9} {'salto':>8}")
        for t, d, pc, c, pct in rows:
            flag = "  ← cambio ticker?" if abs(pct) > 60 else ""
            print(f"  {t:<7} {str(d):<12} {pc:>9.2f} {c:>9.2f} {pct:>7.1f}%{flag}")
        warn(len(rows))
    else:
        print("\n  ✓ Nessun salto giornaliero > 20%")

    # ── C. Candele anomale isolate (fat finger) ──────────────
    section("C. CANDELE ANOMALE ISOLATE (spike che rientra subito = dato sporco)")
    rows = conn.execute("""
        WITH w AS (
            SELECT ticker, ts, high, low, close,
                   LAG(close)  OVER (PARTITION BY ticker ORDER BY ts) AS prev_c,
                   LEAD(close) OVER (PARTITION BY ticker ORDER BY ts) AS next_c
            FROM candles
        )
        SELECT ticker, ts, prev_c, close, next_c
        FROM w
        WHERE prev_c IS NOT NULL AND next_c IS NOT NULL AND prev_c > 0 AND next_c > 0
          AND ( (close > 1.35 * prev_c AND close > 1.35 * next_c)
             OR (close < 0.65 * prev_c AND close < 0.65 * next_c) )
        ORDER BY ticker, ts LIMIT 30
    """).fetchall()
    if rows:
        print(f"\n  Spike isolati trovati: {len(rows)}")
        for t, ts, pc, c, nc in rows:
            print(f"    {t:<6} {ts}  prima={pc:.2f}  PICCO={c:.2f}  dopo={nc:.2f}")
        crit(len(rows))
    else:
        print("\n  ✓ Nessuno spike isolato anomalo")

    # ── D. Prezzi congelati ──────────────────────────────────
    section("D. PREZZI CONGELATI (>=12 candele identiche di fila con volume>0)")
    rows = conn.execute("""
        WITH grp AS (
            SELECT ticker, ts, close, volume,
                   ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY ts)
                 - ROW_NUMBER() OVER (PARTITION BY ticker, close ORDER BY ts) AS island
            FROM candles
        )
        SELECT ticker, close, COUNT(*) AS run_len,
               MIN(ts) AS dal, MAX(ts) AS al, SUM(volume) AS vol_tot
        FROM grp
        GROUP BY ticker, close, island
        HAVING COUNT(*) >= 12 AND SUM(volume) > 0
        ORDER BY run_len DESC LIMIT 20
    """).fetchall()
    if rows:
        print(f"\n  Sequenze di prezzo congelato: {len(rows)}")
        for t, c, n, dal, al, vol in rows:
            print(f"    {t:<6} close={c:.2f}  x{n} candele  {dal} → {al}  vol={int(vol):,}")
        warn(len(rows))
    else:
        print("\n  ✓ Nessun prezzo congelato sospetto")

    # ── E. Coerenza indicatori ───────────────────────────────
    section("E. COERENZA INDICATORI")
    bb_bad = conn.execute("""
        SELECT COUNT(*) FROM candles
        WHERE bb_lower IS NOT NULL AND bb_mid IS NOT NULL AND bb_upper IS NOT NULL
          AND (bb_lower > bb_mid + 0.001 OR bb_mid > bb_upper + 0.001)
    """).fetchone()[0]
    atr_bad = conn.execute("SELECT COUNT(*) FROM candles WHERE atr < 0").fetchone()[0]
    rsi_bad = conn.execute("SELECT COUNT(*) FROM candles WHERE rsi < 0 OR rsi > 100.001").fetchone()[0]
    print(f"\n  Bollinger non ordinate (lower>mid>upper): {bb_bad}")
    print(f"  ATR negativo:                            {atr_bad}")
    print(f"  RSI fuori [0,100]:                       {rsi_bad}")
    if bb_bad or atr_bad or rsi_bad:
        crit(bb_bad + atr_bad + rsi_bad)
    else:
        print("  ✓ Indicatori internamente coerenti")

    # ── F. NaN indicatori a metà serie ───────────────────────
    section("F. NaN INDICATORI DOPO IL WARMUP (buchi anomali a metà serie)")
    # Per ogni ticker, conta NaN di rsi DOPO la 300esima candela (warmup ampiamente superato)
    rows = conn.execute("""
        WITH numbered AS (
            SELECT ticker, ts, rsi, macd, ema_200,
                   ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY ts) AS rn
            FROM candles
        )
        SELECT ticker, COUNT(*) AS nan_dopo_warmup
        FROM numbered
        WHERE rn > 300 AND (rsi IS NULL OR macd IS NULL OR ema_200 IS NULL)
        GROUP BY ticker
        HAVING COUNT(*) > 0
        ORDER BY nan_dopo_warmup DESC LIMIT 20
    """).fetchall()
    if rows:
        print(f"\n  Ticker con NaN dopo le prime 300 candele:")
        for t, n in rows:
            print(f"    {t:<6} {n} candele con indicatore mancante")
        warn(len(rows))
    else:
        print("\n  ✓ Nessun buco negli indicatori dopo il warmup")

    # ── G. Tabella macro ─────────────────────────────────────
    section("G. TABELLA MACRO")
    macro_exists = conn.execute("""
        SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'macro'
    """).fetchone()[0]
    if not macro_exists:
        print("\n  ! Tabella macro non presente")
    else:
        stats = conn.execute("""
            SELECT
                COUNT(*) AS n,
                SUM(CASE WHEN vix IS NULL THEN 1 ELSE 0 END) AS vix_nan,
                SUM(CASE WHEN fed_rate IS NULL THEN 1 ELSE 0 END) AS fed_nan,
                MIN(vix), MAX(vix), MIN(fed_rate), MAX(fed_rate),
                MIN(unemployment), MAX(unemployment)
            FROM macro
        """).fetchone()
        print(f"\n  Righe: {stats[0]:,}")
        print(f"  VIX NaN: {stats[1]}   Fed NaN: {stats[2]}")
        print(f"  VIX range:  {stats[3]:.1f} → {stats[4]:.1f}   (plausibile ~9-90)")
        print(f"  Fed range:  {stats[5]:.2f} → {stats[6]:.2f}%  (plausibile 0-6)")
        print(f"  Disocc.:    {stats[7]:.1f} → {stats[8]:.1f}%  (plausibile 3-15)")
        bad_macro = 0
        if stats[3] < 5 or stats[4] > 100:
            print("  ! VIX fuori range plausibile"); bad_macro += 1
        if stats[5] < 0 or stats[6] > 10:
            print("  ! Fed rate fuori range plausibile"); bad_macro += 1
        if bad_macro == 0:
            print("  ✓ Valori macro nei range plausibili")
        else:
            warn(bad_macro)

    # ── H. Outlier di volume ─────────────────────────────────
    section("H. OUTLIER DI VOLUME (candela con volume >50x la mediana del ticker)")
    rows = conn.execute("""
        WITH med AS (
            SELECT ticker, MEDIAN(volume) AS med_vol
            FROM candles WHERE volume > 0 GROUP BY ticker
        )
        SELECT c.ticker, c.ts, c.volume, m.med_vol,
               ROUND(c.volume / NULLIF(m.med_vol,0), 0) AS volte
        FROM candles c JOIN med m ON c.ticker = m.ticker
        WHERE m.med_vol > 0 AND c.volume > 50 * m.med_vol
        ORDER BY volte DESC LIMIT 15
    """).fetchall()
    if rows:
        print(f"\n  Candele con volume estremo (>50x mediana): {len(rows)} (mostro top 15)")
        for t, ts, vol, med, volte in rows:
            print(f"    {t:<6} {ts}  vol={int(vol):,}  (mediana {int(med):,}, {int(volte)}x)")
        print("\n  Nota: spesso legittimi (earnings, news). Da guardare solo se isolati e senza movimento prezzo.")
        warn(len(rows))
    else:
        print("\n  ✓ Nessun outlier di volume estremo")

    # ── Verdetto ─────────────────────────────────────────────
    section("VERDETTO")
    print(f"\n  Problemi critici (da correggere):   {issues['critici']}")
    print(f"  Da guardare (spesso legittimi):     {issues['da_guardare']}")
    print()
    if issues["critici"] == 0:
        print("  ✅  Nessun problema critico — database solido")
    else:
        print("  ⚠️   Ci sono problemi critici da esaminare")
    print()

    conn.close()


if __name__ == "__main__":
    main()
