"""
Tab "Indicatori per settore" — confronto di un indicatore tra i titoli di un settore.

Scegli un indicatore e un settore: vedi la stessa misura per ogni titolo del
settore, sovrapposta. Utile per capire chi è ipercomprato/ipervenduto o chi
guida il movimento. Il menu offre solo gli indicatori confrontabili tra titoli.
Il grafico è riempito dal callback in `callbacks/register.py`.
"""
from dash import dcc, html
import dash_bootstrap_components as dbc

from shared.config.settings import TICKERS_BY_SECTOR
from dashboard.components.options import PERIOD_OPTIONS
from dashboard.indicators.catalog import comparable_options
from dashboard.charts.theme import ACCENT, TEXT_MUTED

_SECTOR_OPTIONS = [{"label": s, "value": s} for s in TICKERS_BY_SECTOR.keys()]
_FIRST_SECTOR = next(iter(TICKERS_BY_SECTOR.keys()))


def sector_indicator_tab() -> dbc.Tab:
    return dbc.Tab(label="🧭  Indicatori per settore", tab_id="sector-ind", children=[
        html.P("Lo stesso indicatore per tutti i titoli di un settore, sovrapposti. "
               "Confronta a colpo d'occhio quali titoli sono ipercomprati o ipervenduti, "
               "e chi sta guidando il movimento. Clicca un titolo nella legenda per isolarlo.",
               style={"color": TEXT_MUTED, "fontSize": "13px", "marginTop": "16px"}),

        dbc.Row([
            dbc.Col([
                dbc.Label("Indicatore", style={"fontSize": "12px", "color": TEXT_MUTED}),
                dcc.Dropdown(id="sector-ind-indicator", options=comparable_options(),
                             value="rsi", clearable=False),
            ], width=4),
            dbc.Col([
                dbc.Label("Settore", style={"fontSize": "12px", "color": TEXT_MUTED}),
                dcc.Dropdown(id="sector-ind-sector", options=_SECTOR_OPTIONS,
                             value=_FIRST_SECTOR, clearable=False),
            ], width=4),
            dbc.Col([
                dbc.Label("Periodo", style={"fontSize": "12px", "color": TEXT_MUTED}),
                dcc.Dropdown(id="sector-ind-period", options=PERIOD_OPTIONS,
                             value=365, clearable=False),
            ], width=4),
        ], className="mt-3 mb-2 g-3"),

        dcc.Loading(
            dcc.Graph(id="sector-ind-chart"),
            type="circle", color=ACCENT,
        ),
    ])
