"""
Intestazione della dashboard.

Titolo a sinistra, contatori (candele totali, numero ticker, settori) a destra.
Riceve `db_stats` calcolato all'avvio dell'app.
"""
import pandas as pd
from dash import html
import dash_bootstrap_components as dbc

from dashboard.charts.theme import ACCENT, GREEN, TEXT_MUTED


def make_header(db_stats: pd.DataFrame) -> dbc.Row:
    total_candles = db_stats["n"].sum()
    n_tickers = db_stats["ticker"].nunique()

    return dbc.Row([
        dbc.Col([
            html.H4("AI Market Predictor",
                    className="mb-0", style={"color": ACCENT, "fontWeight": "700"}),
            html.Small("Dashboard — esplorazione dati Fase 1",
                       style={"color": "#64748b"}),
        ], width=6),
        dbc.Col([
            html.Div([
                html.Span(f"{total_candles:,} candele",
                          style={"color": GREEN, "marginRight": "16px", "fontWeight": "600"}),
                html.Span(f"{n_tickers} ticker · 11 settori",
                          style={"color": TEXT_MUTED}),
            ], className="text-end mt-2"),
        ], width=6),
    ], className="py-3 border-bottom border-secondary mb-3")
