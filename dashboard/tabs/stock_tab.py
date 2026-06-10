"""
Tab "Azione" — la pagina di dettaglio di un singolo titolo.

Scegli ticker e periodo, poi aggiungi/togli quanti indicatori vuoi dal menu:
il grafico si ricompone con il prezzo in alto, gli overlay sul prezzo e un
pannello per ogni oscillatore. Mostra i valori MEMORIZZATI nel database.
Il grafico è riempito dal callback in `callbacks/register.py`.
"""
from dash import dcc, html
import dash_bootstrap_components as dbc

from dashboard.components.options import TICKER_OPTIONS, PERIOD_OPTIONS
from dashboard.indicators.catalog import chartable_options
from dashboard.charts.theme import ACCENT, TEXT_MUTED

# Indicatori mostrati di default all'apertura
_DEFAULT = ["ema", "rsi", "macd"]


def stock_tab() -> dbc.Tab:
    return dbc.Tab(label="🔬  Azione", tab_id="stock", children=[
        html.P("La scheda completa di un titolo: tutti gli indicatori che abbiamo "
               "calcolato, nel tempo. Aggiungi o togli indicatori dal menu — gli "
               "overlay (medie, bande) finiscono sul prezzo, gli oscillatori in un "
               "pannello a parte, i pattern come frecce.",
               style={"color": TEXT_MUTED, "fontSize": "13px", "marginTop": "16px"}),

        dbc.Row([
            dbc.Col([
                dbc.Label("Ticker", style={"fontSize": "12px", "color": TEXT_MUTED}),
                dcc.Dropdown(id="stock-select", options=TICKER_OPTIONS,
                             value="AAPL", clearable=False),
            ], width=3),
            dbc.Col([
                dbc.Label("Periodo", style={"fontSize": "12px", "color": TEXT_MUTED}),
                dcc.Dropdown(id="stock-period", options=PERIOD_OPTIONS,
                             value=365, clearable=False),
            ], width=3),
            dbc.Col([
                dbc.Label("Indicatori da mostrare", style={"fontSize": "12px", "color": TEXT_MUTED}),
                dcc.Dropdown(id="stock-indicators", options=chartable_options(),
                             value=_DEFAULT, multi=True,
                             placeholder="Aggiungi indicatori..."),
            ], width=6),
        ], className="mt-3 mb-2 g-3"),

        dcc.Loading(
            dcc.Graph(id="stock-chart", config={"scrollZoom": True}),
            type="circle", color=ACCENT,
        ),
    ])
