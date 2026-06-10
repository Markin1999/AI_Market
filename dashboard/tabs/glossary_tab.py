"""
Tab "Indicatori" — il glossario, generato dal catalogo.

Per ogni indicatore mostra: nome, scala dei valori, "cos'è" e "come si legge".
Le card sono raggruppate per categoria. È una vista statica: si costruisce
una volta dal catalogo, senza callback. Aggiungi una voce in
`indicators/catalog.py` e qui compare da sola.
"""
from dash import html
import dash_bootstrap_components as dbc

from dashboard.indicators.catalog import by_category, CATEGORY_COLORS
from dashboard.charts.theme import BG_PANEL, BORDER, TEXT, TEXT_MUTED


def _indicator_card(ind, color: str) -> dbc.Col:
    badge = html.Span(
        ind.unit or ("pattern" if ind.pattern else ""),
        style={"backgroundColor": color + "22", "color": color,
               "fontSize": "11px", "padding": "1px 8px", "borderRadius": "10px",
               "marginLeft": "8px", "fontWeight": "600"},
    ) if (ind.unit or ind.pattern) else None

    return dbc.Col(html.Div([
        html.Div([
            html.Span(ind.name, style={"color": TEXT, "fontWeight": "600", "fontSize": "14px"}),
            badge,
        ], className="mb-2"),
        html.Div(ind.short, style={"color": TEXT_MUTED, "fontSize": "12.5px",
                                   "lineHeight": "1.45", "marginBottom": "8px"}),
        html.Div([
            html.Span("Come si legge: ", style={"color": color, "fontSize": "12px", "fontWeight": "600"}),
            html.Span(ind.how, style={"color": "#cbd5e1", "fontSize": "12.5px", "lineHeight": "1.45"}),
        ]),
        html.Div(", ".join(ind.cols),
                 style={"color": "#475569", "fontSize": "11px", "marginTop": "8px",
                        "fontFamily": "monospace"}),
    ], style={"backgroundColor": BG_PANEL, "border": f"1px solid {BORDER}",
              "borderLeft": f"3px solid {color}", "borderRadius": "8px",
              "padding": "14px", "height": "100%"}), md=6, lg=4, className="mb-3")


def glossary_tab() -> dbc.Tab:
    sections = []
    for category, indicators in by_category().items():
        if not indicators:
            continue
        color = CATEGORY_COLORS.get(category, "#94a3b8")
        sections.append(html.H5(category, style={
            "color": color, "fontWeight": "700", "marginTop": "20px",
            "marginBottom": "12px", "fontSize": "16px",
        }))
        sections.append(dbc.Row(
            [_indicator_card(ind, color) for ind in indicators],
            className="g-2",
        ))

    return dbc.Tab(label="📚  Indicatori", tab_id="glossary", children=[
        html.P("Tutti gli indicatori calcolati nel database, spiegati: cosa misurano "
               "e come si interpretano. In fondo a ogni card, in grigio, i nomi delle "
               "colonne nel database.",
               style={"color": TEXT_MUTED, "fontSize": "13px", "marginTop": "16px",
                      "marginBottom": "8px"}),
        html.Div(sections),
    ])
