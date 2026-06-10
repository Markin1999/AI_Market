"""
Connessione unica al database DuckDB — sola lettura.

La dashboard non scrive MAI sul database: apre una connessione read-only e la
riusa per tutte le query. Centralizzata qui, c'è un solo punto da cambiare se
un domani il percorso del DB o la modalità di accesso cambiano.

`read_only=True` permette anche di aprire il DB mentre un altro processo
(es. uno script della pipeline) lo sta leggendo, senza conflitti di lock.
"""
import duckdb

from shared.config.settings import DB_PATH

_conn = None


def get_connection() -> duckdb.DuckDBPyConnection:
    """Restituisce la connessione condivisa, creandola alla prima chiamata."""
    global _conn
    if _conn is None:
        _conn = duckdb.connect(str(DB_PATH), read_only=True)
    return _conn
