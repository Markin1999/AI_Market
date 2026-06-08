import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / "config" / ".env")

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY", "")
FRED_API_KEY    = os.getenv("FRED_API_KEY", "")

# Universo titoli — 66 ticker su 11 settori S&P500
TICKERS_BY_SECTOR = {
    "Technology":              ["AAPL", "MSFT", "NVDA", "AMD", "GOOGL", "META"],
    "Financials":              ["JPM", "BAC", "GS", "MS", "BRK.B", "C"],
    "Health Care":             ["JNJ", "UNH", "PFE", "ABBV", "MRK", "LLY"],
    "Consumer Discretionary":  ["AMZN", "TSLA", "HD", "MCD", "NKE", "SBUX"],
    "Consumer Staples":        ["PG", "KO", "PEP", "WMT", "COST", "CL"],
    "Energy":                  ["XOM", "CVX", "COP", "SLB", "EOG", "PSX"],
    "Industrials":             ["CAT", "BA", "HON", "UPS", "GE", "LMT"],
    "Materials":               ["LIN", "APD", "NEM", "FCX", "ECL", "VMC"],
    "Real Estate":             ["AMT", "PLD", "CCI", "EQIX", "SPG", "DLR"],
    "Utilities":               ["NEE", "DUK", "SO", "AEP", "EXC", "XEL"],
    "Communication Services":  ["NFLX", "DIS", "CMCSA", "T", "CHTR", "VZ"],
}

ALL_TICKERS = [t for tickers in TICKERS_BY_SECTOR.values() for t in tickers]

TICKER_TO_SECTOR = {
    ticker: sector
    for sector, tickers in TICKERS_BY_SECTOR.items()
    for ticker in tickers
}

# Parametri dati
CANDLE_TIMESPAN = "minute"
CANDLE_MULTIPLIER = 15        # candele da 15 minuti
HISTORY_YEARS = 5             # anni di storico (limite piano Polygon Starter)
DB_PATH = ROOT_DIR / "data" / "raw" / "market.duckdb"

# Indicatori tecnici
RSI_PERIOD = 14
EMA_PERIODS = [20, 50, 200]
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
BB_PERIOD = 20
BB_STD = 2
ATR_PERIOD = 14
