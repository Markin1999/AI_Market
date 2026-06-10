"""
Tab "Settori nel tempo".

Selettore del periodo + il grafico a linee della crescita settoriale.
Il grafico è riempito dal callback in `callbacks/register.py`.
"""
from dash import dcc, html
import dash_bootstrap_components as dbc

from dashboard.charts.theme import ACCENT, TEXT_MUTED


def growth_tab() -> dbc.Tab:
    return dbc.Tab(label="📊  Settori nel tempo", tab_id="growth", children=[
        html.P("Come è cresciuto ogni settore nel tempo. Ogni linea parte da 0% "
               "all'inizio del periodo: così confronti chi è salito di più e chi di meno. "
               "Clicca un settore nella legenda per nasconderlo o isolarlo.",
               style={"color": TEXT_MUTED, "fontSize": "13px", "marginTop": "16px"}),
        dbc.Row([
            dbc.Col([
                dbc.Label("Periodo", style={"fontSize": "12px", "color": TEXT_MUTED}),
                dcc.Dropdown(id="growth-period", value=730, clearable=False,
                             style={"width": "200px"}, options=[
                    {"label": "6 mesi", "value": 180},
                    {"label": "1 anno", "value": 365},
                    {"label": "2 anni", "value": 730},
                    {"label": "3 anni", "value": 1095},
                    {"label": "Tutto", "value": 3000},
                ]),
            ], width=3),
        ], className="mt-2 mb-2"),
        dcc.Loading(
            dcc.Graph(id="growth-chart"),
            type="circle", color=ACCENT,
        ),
    ])
