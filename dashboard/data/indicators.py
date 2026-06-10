"""
Caricamento degli indicatori MEMORIZZATI nel database.

A differenza di `data/candles.py` (che RICALCOLA gli indicatori sul timeframe
mostrato), qui leggiamo i valori così come sono STATI SALVATI nel DB — cioè
"tutti gli indicatori che abbiamo calcolato". Per restare veloci e leggibili
li campioniamo: per ogni intervallo (bucket) prendiamo il valore di chiusura.

    • indicatori continui  → valore all'ultima candela del bucket   (arg_max ... ts)
    • pattern candele      → il segnale più forte del bucket         (arg_max ... abs)

Due funzioni:
    load_stock_full      → tutti gli indicatori di UN titolo nel tempo
    load_sector_indicator→ UN indicatore di TUTTI i titoli di un settore
"""
import pandas as pd

from dashboard.data.connection import get_connection
from dashboard.data.candles import choose_bucket
from dashboard.indicators.catalog import (
    ALL_INDICATOR_COLUMNS, ALL_COLUMNS, PATTERN_COLUMNS,
)

_stock_cache: dict[tuple[str, int], tuple[pd.DataFrame, str]] = {}
_sector_cache: dict[tuple[str, tuple, int], tuple[pd.DataFrame, str]] = {}


def load_stock_full(ticker: str, days: int) -> tuple[pd.DataFrame, str]:
    """OHLCV + TUTTI gli indicatori memorizzati di un titolo, campionati per bucket."""
    key = (ticker, days)
    if key in _stock_cache:
        return _stock_cache[key]

    bucket_sql, label = choose_bucket(days)

    # Per ogni colonna scegliamo l'aggregazione giusta
    agg = []
    for c in ALL_INDICATOR_COLUMNS:
        if c in PATTERN_COLUMNS:
            agg.append(f"arg_max({c}, abs({c})) AS {c}")   # il segnale più forte del bucket
        else:
            agg.append(f"arg_max({c}, ts) AS {c}")          # valore a chiusura bucket
    agg_sql = ", ".join(agg)

    df = get_connection().execute(f"""
        SELECT time_bucket(INTERVAL '{bucket_sql}', ts) AS ts,
               arg_min(open, ts)  AS open,
               max(high)          AS high,
               min(low)           AS low,
               arg_max(close, ts) AS close,
               sum(volume)        AS volume,
               arg_max(vwap, ts)  AS vwap,
               {agg_sql}
        FROM candles
        WHERE ticker = ?
          AND ts >= (SELECT MAX(ts) FROM candles WHERE ticker = ?) - INTERVAL (?) DAY
        GROUP BY 1
        ORDER BY 1
    """, [ticker, ticker, days]).df()

    _stock_cache[key] = (df, label)
    return df, label


def load_sector_indicator(col: str, tickers: list[str], days: int) -> tuple[pd.DataFrame, str]:
    """
    Un singolo indicatore (colonna `col`) per ogni ticker del settore, nel tempo.
    `col` è validato contro il catalogo: solo colonne note possono entrare nella query.
    """
    if col not in ALL_COLUMNS:
        raise ValueError(f"Colonna indicatore non valida: {col}")

    key = (col, tuple(tickers), days)
    if key in _sector_cache:
        return _sector_cache[key]

    bucket_sql, label = choose_bucket(days)
    placeholders = ", ".join(["?"] * len(tickers))

    df = get_connection().execute(f"""
        SELECT time_bucket(INTERVAL '{bucket_sql}', ts) AS ts,
               ticker,
               arg_max({col}, ts) AS value
        FROM candles
        WHERE ticker IN ({placeholders})
          AND ts >= (SELECT MAX(ts) FROM candles) - INTERVAL (?) DAY
        GROUP BY 1, 2
        ORDER BY 1
    """, [*tickers, days]).df()

    _sector_cache[key] = (df, label)
    return df, label
