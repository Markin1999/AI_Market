"""
Statistiche di stato del database.

Una sola query: per ogni ticker, quante candele ci sono e qual è il periodo
coperto (prima e ultima data). Alimenta la tab "Database" e i contatori
dell'intestazione.
"""
import pandas as pd

from dashboard.data.connection import get_connection


def load_db_stats() -> pd.DataFrame:
    """Candele per ticker + periodo coperto, ordinate per settore."""
    return get_connection().execute("""
        SELECT ticker, sector, COUNT(*) AS n,
               MIN(ts)::DATE AS dal, MAX(ts)::DATE AS al
        FROM candles
        GROUP BY ticker, sector
        ORDER BY sector, ticker
    """).df()
