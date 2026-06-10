"""
Tab "Database" — stato dei dati scaricati.

Quattro card di riepilogo in alto (candele totali, ticker, primo e ultimo dato)
e una tabella scrollabile, raggruppata per settore, con quante candele e quale
periodo copre ogni titolo. È una vista statica: costruita una volta dai
`db_stats` calcolati all'avvio, non ha callback.
"""
import pandas as pd
from dash import html
import dash_bootstrap_components as dbc

from dashboard.charts.theme import ACCENT, GREEN, TEXT_MUTED, BG_PANEL, BORDER, SECTOR_COLORS


def _summary_cards(db_stats: pd.DataFrame) -> dbc.Row:
    def card(value, label, color):
        return dbc.Col(dbc.Card(dbc.CardBody([
            html.H3(str(value), style={"color": color, "margin": "0"}),
            html.Small(label, style={"color": TEXT_MUTED}),
        ])), width=3)

    return dbc.Row([
        card(f"{db_stats['n'].sum():,}",       "Candele totali", ACCENT),
        card(db_stats["ticker"].nunique(),     "Ticker",         GREEN),
        card(db_stats["dal"].min(),            "Primo dato",     "#f59e0b"),
        card(db_stats["al"].max(),             "Ultimo dato",    "#f59e0b"),
    ], className="mt-3 mb-3 g-2")


def _table_rows(db_stats: pd.DataFrame) -> list:
    rows = []
    current_sector = None
    for _, row in db_stats.iterrows():
        if row["sector"] != current_sector:
            current_sector = row["sector"]
            color = SECTOR_COLORS.get(current_sector, "#6b7280")
            rows.append(html.Tr([
                html.Td(current_sector, colSpan=4,
                        style={"backgroundColor": color + "22", "color": color,
                               "fontWeight": "600", "padding": "6px 12px",
                               "fontSize": "12px", "letterSpacing": "0.05em"})
            ]))
        rows.append(html.Tr([
            html.Td(row["ticker"], style={"padding": "4px 12px", "fontWeight": "500"}),
            html.Td(f"{row['n']:,}", style={"textAlign": "right", "padding": "4px 12px"}),
            html.Td(str(row["dal"]), style={"padding": "4px 12px", "color": TEXT_MUTED}),
            html.Td(str(row["al"]),  style={"padding": "4px 12px", "color": TEXT_MUTED}),
        ], style={"borderBottom": f"1px solid {BORDER}"}))
    return rows


def database_tab(db_stats: pd.DataFrame) -> dbc.Tab:
    return dbc.Tab(label="💾  Database", tab_id="db", children=[
        html.P("Lo stato dei dati scaricati: quante candele abbiamo per ogni titolo "
               "e il periodo coperto. Serve a verificare che il database sia completo "
               "prima di addestrare il modello.",
               style={"color": TEXT_MUTED, "fontSize": "13px", "marginTop": "16px"}),

        _summary_cards(db_stats),

        html.Div([
            html.Table([
                html.Thead(html.Tr([
                    html.Th("Ticker",  style={"padding": "8px 12px"}),
                    html.Th("Candele", style={"padding": "8px 12px", "textAlign": "right"}),
                    html.Th("Dal",     style={"padding": "8px 12px"}),
                    html.Th("Al",      style={"padding": "8px 12px"}),
                ]), style={"backgroundColor": "#1e293b", "fontSize": "12px",
                           "color": TEXT_MUTED, "textTransform": "uppercase",
                           "position": "sticky", "top": "0"}),
                html.Tbody(_table_rows(db_stats), style={"fontSize": "13px"}),
            ], style={"width": "100%", "borderCollapse": "collapse"}),
        ], style={"maxHeight": "520px", "overflowY": "auto",
                  "backgroundColor": BG_PANEL, "borderRadius": "8px",
                  "border": f"1px solid {BORDER}"}),
    ])
