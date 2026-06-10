"""
Tab "Heatmap settoriale".

Selettore del periodo + la heatmap. Il grafico è riempito dal callback in
`callbacks/register.py`.
"""
from dash import dcc, html
import dash_bootstrap_components as dbc

from dashboard.charts.theme import ACCENT, TEXT_MUTED


def heatmap_tab() -> dbc.Tab:
    return dbc.Tab(label="🟩  Heatmap settoriale", tab_id="heatmap", children=[
        html.P("Tutti i 66 titoli colorati in base alla performance del periodo scelto. "
               "Verde = il prezzo è salito, rosso = sceso. Ogni riga è un settore: "
               "serve a vedere a colpo d'occhio quali settori si muovono insieme.",
               style={"color": TEXT_MUTED, "fontSize": "13px", "marginTop": "16px"}),
        dbc.Row([
            dbc.Col([
                dbc.Label("Periodo", style={"fontSize": "12px", "color": TEXT_MUTED}),
                dcc.Dropdown(id="heatmap-period", value=5, clearable=False,
                             style={"width": "200px"}, options=[
                    {"label": "Oggi",     "value": 1},
                    {"label": "5 giorni", "value": 5},
                    {"label": "1 mese",   "value": 30},
                    {"label": "3 mesi",   "value": 90},
                    {"label": "6 mesi",   "value": 180},
                    {"label": "1 anno",   "value": 365},
                ]),
            ], width=3),
        ], className="mt-3 mb-2"),
        dcc.Loading(
            dcc.Graph(id="heatmap-chart"),
            type="circle", color=ACCENT,
        ),
    ])
