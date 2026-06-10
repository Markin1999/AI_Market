"""
Caricamento candele con aggregazione adattiva del timeframe + cache.

PERCHÉ L'AGGREGAZIONE
    Su 5 anni le candele a 15 minuti sono decine di migliaia per ticker:
    disegnarle tutte renderebbe il grafico lentissimo e illeggibile. Per
    periodi lunghi le aggreghiamo lato database (1 ora, 4 ore, giornaliere,
    settimanali) con `time_bucket`, così a schermo arrivano poche centinaia
    di candele già pronte.

PERCHÉ LA CACHE
    Ogni volta che l'utente attiva/disattiva un overlay (EMA, Bollinger) Dash
    richiama il grafico. Senza cache rifaremmo query + ricalcolo indicatori
    ogni volta. Con la cache, per la stessa coppia (ticker, periodo) il lavoro
    si fa UNA volta sola: cambiare overlay diventa istantaneo.
"""
import pandas as pd

from dashboard.data.connection import get_connection
from shared.indicators.calculate import add_indicators

# Cache in memoria: chiave (ticker, giorni) → (DataFrame, etichetta_timeframe)
_cache: dict[tuple[str, int], tuple[pd.DataFrame, str]] = {}

# Indicatori che il grafico a candele disegna (riempiti di NaN se mancano)
_CHART_INDICATORS = [
    "rsi", "macd", "macd_signal", "macd_hist",
    "ema_20", "ema_50", "ema_200",
    "bb_upper", "bb_mid", "bb_lower", "atr",
]


def choose_bucket(days: int) -> tuple[str, str]:
    """
    Sceglie l'aggregazione in base al periodo richiesto.
    Restituisce (intervallo_SQL, etichetta_leggibile).
    """
    if days <= 8:    return "15 minutes", "15 min"
    if days <= 31:   return "1 hour",     "1 ora"
    if days <= 130:  return "4 hours",    "4 ore"
    if days <= 800:  return "1 day",      "giornaliere"
    return "1 week", "settimanali"


def load_candles(ticker: str, days: int = 90) -> tuple[pd.DataFrame, str]:
    """
    Carica le candele aggregate per `ticker` sugli ultimi `days` giorni,
    ricalcola gli indicatori sul timeframe mostrato e mette in cache il risultato.
    """
    key = (ticker, days)
    if key in _cache:
        return _cache[key]

    bucket_sql, label = choose_bucket(days)

    df = get_connection().execute(f"""
        SELECT time_bucket(INTERVAL '{bucket_sql}', ts) AS ts,
               arg_min(open, ts)  AS open,
               max(high)          AS high,
               min(low)           AS low,
               arg_max(close, ts) AS close,
               sum(volume)        AS volume
        FROM candles
        WHERE ticker = ?
          AND ts >= (SELECT MAX(ts) FROM candles WHERE ticker = ?) - INTERVAL (?) DAY
        GROUP BY 1
        ORDER BY 1
    """, [ticker, ticker, days]).df()

    if df.empty:
        _cache[key] = (df, label)
        return df, label

    # Gli indicatori vanno ricalcolati sul timeframe VISUALIZZATO: l'RSI su
    # candele giornaliere è diverso dall'RSI a 15 min — qui usiamo quello giusto.
    df = add_indicators(df)
    for c in _CHART_INDICATORS:
        if c not in df.columns:
            df[c] = float("nan")

    _cache[key] = (df, label)
    return df, label
