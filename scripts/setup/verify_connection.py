"""
Passo 1 — Verifica connessione Polygon.io e accesso ai dati.
Esegui dopo aver inserito la API key in config/.env
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.settings import POLYGON_API_KEY, ALL_TICKERS, TICKERS_BY_SECTOR
import requests


BASE_URL = "https://api.polygon.io"


def check_api_key():
    if not POLYGON_API_KEY or POLYGON_API_KEY == "inserisci_qui_la_tua_key":
        print("✗ API key non configurata.")
        print("  → Apri config/.env e inserisci la tua POLYGON_API_KEY")
        return False

    url = f"{BASE_URL}/v2/aggs/ticker/AAPL/range/15/minute/2024-01-02/2024-01-02"
    params = {"apiKey": POLYGON_API_KEY, "limit": 1}
    resp = requests.get(url, params=params, timeout=10)

    if resp.status_code == 200:
        data = resp.json()
        if data.get("status") in ("OK", "DELAYED"):
            print("✓ Connessione a Polygon.io riuscita")
            return True
        elif data.get("status") == "NOT_AUTHORIZED":
            print("✗ API key non autorizzata — verifica il piano Polygon.io")
            return False

    if resp.status_code == 403:
        print("✗ API key non valida (403 Forbidden)")
        return False

    print(f"✗ Risposta inattesa: {resp.status_code} — {resp.text[:200]}")
    return False


def check_historical_access():
    """Verifica accesso allo storico a 15 min su 5 anni (limite piano Starter)."""
    url = f"{BASE_URL}/v2/aggs/ticker/AAPL/range/15/minute/2022-03-15/2022-03-15"
    params = {"apiKey": POLYGON_API_KEY, "limit": 50, "adjusted": "true", "sort": "asc"}
    resp = requests.get(url, params=params, timeout=10)

    if resp.status_code == 403:
        print("✗ Accesso storico negato — il piano non copre 4 anni fa")
        return False

    if resp.status_code != 200:
        print(f"✗ Risposta inattesa: {resp.status_code}")
        return False

    data = resp.json()
    count = data.get("resultsCount", 0)
    if count > 0:
        print(f"✓ Accesso storico OK — {count} candele 15min per 2022-03-15")
        return True
    else:
        print("! Storico raggiungibile ma 0 candele — verifica date di mercato")
        return True


def check_ticker_availability():
    """Verifica disponibilità di qualche ticker campione."""
    sample = ["AAPL", "MSFT", "NVDA", "JPM", "TSLA"]
    ok = 0
    for ticker in sample:
        url = f"{BASE_URL}/v2/aggs/ticker/{ticker}/range/15/minute/2024-03-15/2024-03-15"
        params = {"apiKey": POLYGON_API_KEY, "limit": 50, "adjusted": "true", "sort": "asc"}
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200 and resp.json().get("resultsCount", 0) > 0:
            ok += 1
        else:
            print(f"  ! Nessun dato per {ticker}")

    print(f"✓ Ticker campione disponibili: {ok}/{len(sample)}")
    return ok >= 3


def print_summary():
    print()
    print("=== Riepilogo configurazione ===")
    print(f"  Ticker totali : {len(ALL_TICKERS)}")
    print(f"  Settori       : {len(TICKERS_BY_SECTOR)}")
    for sector, tickers in TICKERS_BY_SECTOR.items():
        print(f"    {sector:<30} {', '.join(tickers)}")


if __name__ == "__main__":
    print("=== AI Market Predictor — Verifica connessione ===")
    print()

    if not check_api_key():
        sys.exit(1)

    check_historical_access()
    check_ticker_availability()
    print_summary()

    print()
    print("→ Ambiente pronto. Prossimo passo: scarica lo storico con")
    print("  python scripts/data/download_history.py")
