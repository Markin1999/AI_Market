"""
Tab "Grafico" — la schermata principale.

Contiene: i controlli (ticker, periodo, overlay), il pannello a fisarmonica
che spiega ogni elemento del grafico, e il grafico a candele vero e proprio.
Il grafico viene riempito dal callback in `callbacks/register.py`.
"""
from dash import dcc, html
import dash_bootstrap_components as dbc

from shared.config.settings import ALL_TICKERS, TICKER_TO_SECTOR
from dashboard.components.info_card import info_card
from dashboard.charts.theme import ACCENT, TEXT_MUTED

TICKER_OPTIONS = [
    {"label": f"{t}  ({TICKER_TO_SECTOR.get(t, '')})", "value": t}
    for t in ALL_TICKERS
]


def _controls() -> dbc.Row:
    return dbc.Row([
        dbc.Col([
            dbc.Label("Ticker", style={"fontSize": "12px", "color": TEXT_MUTED}),
            dcc.Dropdown(id="ticker-select", options=TICKER_OPTIONS,
                         value="AAPL", clearable=False),
        ], width=3),
        dbc.Col([
            dbc.Label("Periodo", style={"fontSize": "12px", "color": TEXT_MUTED}),
            dcc.Dropdown(id="period-select", value=365, clearable=False, options=[
                {"label": "1 settimana  (15 min)", "value": 7},
                {"label": "1 mese  (1 ora)",       "value": 30},
                {"label": "3 mesi  (4 ore)",       "value": 90},
                {"label": "6 mesi  (giornaliere)", "value": 180},
                {"label": "1 anno  (giornaliere)", "value": 365},
                {"label": "2 anni  (giornaliere)", "value": 730},
                {"label": "5 anni  (settimanali)", "value": 1825},
            ]),
        ], width=3),
        dbc.Col([
            dbc.Label("Overlay", style={"fontSize": "12px", "color": TEXT_MUTED}),
            dbc.Checklist(
                id="indicator-select",
                options=[
                    {"label": "  EMA 20/50/200",  "value": "ema"},
                    {"label": "  Bollinger Bands", "value": "bb"},
                ],
                value=["ema", "bb"], inline=True,
                style={"fontSize": "13px", "marginTop": "6px"},
            ),
        ], width=4),
    ], className="mt-3 mb-2 g-3")


def _explain_panel() -> dbc.Accordion:
    return dbc.Accordion([
        dbc.AccordionItem([
            dbc.Row([
                dbc.Col(info_card("🕯️", "Candele 15 min", "#22c55e",
                    "Ogni candela = 15 minuti di mercato. Verde = il prezzo è salito, "
                    "rossa = sceso. Il corpo va da apertura a chiusura; le linee sottili "
                    "(stoppini) sono il massimo e minimo toccati."), md=6, lg=4),
                dbc.Col(info_card("📊", "Volume", "#64748b",
                    "Quante azioni sono state scambiate in quei 15 minuti. Volume alto "
                    "= movimento affidabile e partecipato. Volume basso = movimento debole."), md=6, lg=4),
                dbc.Col(info_card("📈", "EMA 20 / 50 / 200", "#facc15",
                    "Medie mobili dei prezzi su breve (20), medio (50) e lungo periodo (200). "
                    "Prezzo sopra le linee = tendenza rialzista. La EMA 200 è il trend di fondo."), md=6, lg=4),
                dbc.Col(info_card("🎯", "Bollinger Bands", "#94a3b8",
                    "Banda di volatilità intorno al prezzo. Prezzo vicino alla banda alta "
                    "= forse troppo caro (ipercomprato); vicino alla bassa = forse a sconto "
                    "(ipervenduto)."), md=6, lg=4),
                dbc.Col(info_card("⚡", "RSI (0-100)", "#a78bfa",
                    "Misura la forza del movimento. Sopra 70 (zona rossa) = ipercomprato, "
                    "possibile calo. Sotto 30 (zona verde) = ipervenduto, possibile rimbalzo."), md=6, lg=4),
                dbc.Col(info_card("🔄", "MACD", "#38bdf8",
                    "Segnala i cambi di tendenza. Quando la linea blu incrocia l'arancione "
                    "verso l'alto = momentum rialzista; verso il basso = ribassista. "
                    "Le barre mostrano la forza del segnale."), md=6, lg=4),
            ], className="g-2"),
        ], title="ℹ️  Cosa sto guardando? — clicca per la spiegazione"),
    ], start_collapsed=True, className="mb-3")


def chart_tab() -> dbc.Tab:
    return dbc.Tab(label="📈  Grafico", tab_id="chart", children=[
        _controls(),
        _explain_panel(),
        dcc.Loading(
            dcc.Graph(id="main-chart", config={"scrollZoom": True}),
            type="circle", color=ACCENT,
        ),
    ])
