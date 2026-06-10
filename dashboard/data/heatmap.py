"""
Performance settoriale per la heatmap.

Per ogni ticker calcola la variazione percentuale tra la prima e l'ultima
candela del periodo scelto. Il risultato alimenta la heatmap che colora
tutti i 66 titoli in verde (su) o rosso (giù).
"""
import pandas as pd

from dashboard.data.connection import get_connection


def load_heatmap(days: int = 5) -> pd.DataFrame:
    """Variazione % di ogni ticker negli ultimi `days` giorni."""
    return get_connection().execute("""
        WITH ranked AS (
            SELECT ticker, sector, close, ts,
                   ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY ts ASC)  AS rn_first,
                   ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY ts DESC) AS rn_last
            FROM candles
            WHERE ts >= (SELECT MAX(ts) FROM candles) - INTERVAL (?) DAY
        ),
        first_last AS (
            SELECT ticker, sector,
                   MAX(CASE WHEN rn_first = 1 THEN close END) AS first_close,
                   MAX(CASE WHEN rn_last  = 1 THEN close END) AS last_close
            FROM ranked GROUP BY ticker, sector
        )
        SELECT ticker, sector,
               ROUND((last_close - first_close) / first_close * 100, 2) AS perf_pct
        FROM first_last
        ORDER BY sector, ticker
    """, [days]).df()
