"""
AI Market Predictor — Dashboard (entry point).

Questo è l'UNICO file da lanciare. Mette insieme i pezzi costruiti negli altri
moduli e avvia l'applicazione locale:

    python dashboard/app.py   →   http://127.0.0.1:8050

Architettura (vedi dashboard/README.md per i dettagli):
    data/        → query al database
    charts/      → costruzione dei grafici
    components/  → pezzi di interfaccia riutilizzabili
    tabs/        → le 4 schermate
    callbacks/   → la logica interattiva

Questo file fa solo 4 cose: crea l'app, carica le statistiche una volta,
monta il layout (intestazione + 4 tab) e registra i callback.
"""
import sys
from pathlib import Path

# La root del progetto in sys.path: così funzionano `from shared...` e `from dashboard...`
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import dash
import dash_bootstrap_components as dbc

from dashboard.data.stats import load_db_stats
from dashboard.components.header import make_header
from dashboard.tabs.chart_tab import chart_tab
from dashboard.tabs.stock_tab import stock_tab
from dashboard.tabs.sector_indicator_tab import sector_indicator_tab
from dashboard.tabs.heatmap_tab import heatmap_tab
from dashboard.tabs.growth_tab import growth_tab
from dashboard.tabs.glossary_tab import glossary_tab
from dashboard.tabs.database_tab import database_tab
from dashboard.callbacks.register import register_callbacks
from dashboard.charts.theme import BG_PAGE, FONT

# ── Crea l'app ───────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.CYBORG],
    title="AI Market Predictor",
)

# ── Dati statici caricati una volta sola all'avvio ───────────────────────────
db_stats = load_db_stats()

# ── Layout: intestazione + 4 schede ──────────────────────────────────────────
app.layout = dbc.Container([
    make_header(db_stats),
    dbc.Tabs([
        chart_tab(),
        stock_tab(),
        sector_indicator_tab(),
        heatmap_tab(),
        growth_tab(),
        glossary_tab(),
        database_tab(db_stats),
    ], id="tabs", active_tab="chart"),
], fluid=True, style={"backgroundColor": BG_PAGE, "minHeight": "100vh",
                      "fontFamily": FONT})

# ── Collega i controlli ai grafici ───────────────────────────────────────────
register_callbacks(app)


if __name__ == "__main__":
    print()
    print("  ╔══════════════════════════════════════╗")
    print("  ║   AI Market Predictor — Dashboard    ║")
    print("  ║   http://127.0.0.1:8050              ║")
    print("  ╚══════════════════════════════════════╝")
    print()
    app.run(debug=False, port=8050)
