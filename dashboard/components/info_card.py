"""
Card di spiegazione riutilizzabile.

Un riquadretto con icona, titolo colorato e testo descrittivo. Usato nel
pannello "Cosa sto guardando?" della tab Grafico per spiegare ogni indicatore.
"""
from dash import html

from dashboard.charts.theme import BG_PANEL, BORDER, TEXT_MUTED


def info_card(icon: str, titolo: str, colore: str, testo: str) -> html.Div:
    return html.Div([
        html.Div([
            html.Span(icon, style={"fontSize": "18px", "marginRight": "8px"}),
            html.Span(titolo, style={"color": colore, "fontWeight": "600", "fontSize": "14px"}),
        ], className="mb-1"),
        html.Small(testo, style={"color": TEXT_MUTED, "fontSize": "12px", "lineHeight": "1.4"}),
    ], style={"backgroundColor": BG_PANEL, "border": f"1px solid {BORDER}",
              "borderRadius": "8px", "padding": "12px", "height": "100%"})
