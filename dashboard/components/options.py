"""
Opzioni condivise dei menu a tendina.

Liste usate da più tab (ticker, periodi). Definite una volta sola qui, così
non divergono tra una schermata e l'altra.
"""
from shared.config.settings import ALL_TICKERS, TICKER_TO_SECTOR

# Tutti i ticker, con il settore tra parentesi
TICKER_OPTIONS = [
    {"label": f"{t}  ({TICKER_TO_SECTOR.get(t, '')})", "value": t}
    for t in ALL_TICKERS
]

# Periodo + aggregazione candele che ne deriva (vedi data/candles.choose_bucket)
PERIOD_OPTIONS = [
    {"label": "1 settimana  (15 min)", "value": 7},
    {"label": "1 mese  (1 ora)",       "value": 30},
    {"label": "3 mesi  (4 ore)",       "value": 90},
    {"label": "6 mesi  (giornaliere)", "value": 180},
    {"label": "1 anno  (giornaliere)", "value": 365},
    {"label": "2 anni  (giornaliere)", "value": 730},
    {"label": "5 anni  (settimanali)", "value": 1825},
]
