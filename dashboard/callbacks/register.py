"""
Registrazione dei callback — la logica interattiva della dashboard.

Un callback collega gli input dell'interfaccia (dropdown, checklist) all'output
(un grafico). Quando l'utente cambia un controllo, Dash richiama la funzione
giusta e aggiorna il grafico. Qui sta TUTTA la logica "quando tocchi X, succede Y".

`register_callbacks(app)` va chiamata una volta sola, dopo aver creato l'app.
"""
from dash import Input, Output

from dashboard.charts.candlestick import make_chart
from dashboard.charts.heatmap import make_heatmap
from dashboard.charts.sector_growth import make_sector_growth
from dashboard.charts.stock_detail import make_stock_detail
from dashboard.charts.sector_indicator import make_sector_indicator


def register_callbacks(app):

    # ── Tab Grafico ───────────────────────────────────────────────────────────
    @app.callback(
        Output("main-chart", "figure"),
        Input("ticker-select", "value"),
        Input("period-select", "value"),
        Input("indicator-select", "value"),
    )
    def update_chart(ticker, days, indicators):
        show_ema = "ema" in (indicators or [])
        show_bb  = "bb"  in (indicators or [])
        return make_chart(ticker, days, show_ema, show_bb)

    # ── Tab Azione (dettaglio titolo con indicatori componibili) ──────────────
    @app.callback(
        Output("stock-chart", "figure"),
        Input("stock-select", "value"),
        Input("stock-period", "value"),
        Input("stock-indicators", "value"),
    )
    def update_stock(ticker, days, indicators):
        return make_stock_detail(ticker, days, indicators)

    # ── Tab Indicatori per settore ────────────────────────────────────────────
    @app.callback(
        Output("sector-ind-chart", "figure"),
        Input("sector-ind-indicator", "value"),
        Input("sector-ind-sector", "value"),
        Input("sector-ind-period", "value"),
    )
    def update_sector_indicator(indicator, sector, days):
        return make_sector_indicator(indicator, sector, days)

    # ── Tab Heatmap ───────────────────────────────────────────────────────────
    @app.callback(
        Output("heatmap-chart", "figure"),
        Input("heatmap-period", "value"),
    )
    def update_heatmap(days):
        return make_heatmap(days)

    # ── Tab Settori nel tempo ─────────────────────────────────────────────────
    @app.callback(
        Output("growth-chart", "figure"),
        Input("growth-period", "value"),
    )
    def update_growth(days):
        return make_sector_growth(days)
