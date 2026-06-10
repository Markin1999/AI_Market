"""
Serie storica per il grafico di crescita dei settori.

Estrae la chiusura giornaliera (ultima candela di ogni giorno) di ogni ticker
sugli ultimi `days` giorni. Il grafico poi la normalizza e la media per settore.
"""
import pandas as pd

from dashboard.data.connection import get_connection


def load_sector_growth(days: int) -> pd.DataFrame:
    """Chiusura giornaliera (ultima candela del giorno) per ogni ticker."""
    return get_connection().execute("""
        SELECT date, ticker, sector, close FROM (
            SELECT ts::DATE AS date, ticker, sector, close,
                   ROW_NUMBER() OVER (PARTITION BY ticker, ts::DATE ORDER BY ts DESC) AS rn
            FROM candles
            WHERE ts >= (SELECT MAX(ts) FROM candles) - INTERVAL (?) DAY
        ) WHERE rn = 1
        ORDER BY date
    """, [days]).df()
