"""
Passo 4 — Dashboard interattiva AI Market Predictor
Lancia con: python scripts/viz/dashboard.py
Apri il browser su: http://127.0.0.1:8050
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import duckdb
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc

from config.settings import DB_PATH, TICKERS_BY_SECTOR, ALL_TICKERS, TICKER_TO_SECTOR
from scripts.indicators.calculate import add_indicators

# ── Connessione DB ──────────────────────────────────────────
conn = duckdb.connect(str(DB_PATH), read_only=True)

SECTOR_COLORS = {
    "Technology":             "#6366f1",
    "Financials":             "#0ea5e9",
    "Health Care":            "#10b981",
    "Consumer Discretionary": "#f59e0b",
    "Consumer Staples":       "#84cc16",
    "Energy":                 "#ef4444",
    "Industrials":            "#8b5cf6",
    "Materials":              "#f97316",
    "Real Estate":            "#ec4899",
    "Utilities":              "#14b8a6",
    "Communication Services": "#a78bfa",
}

# ── Dati statici caricati una volta ─────────────────────────
def load_db_stats():
    return conn.execute("""
        SELECT ticker, sector, COUNT(*) AS n,
               MIN(ts)::DATE AS dal, MAX(ts)::DATE AS al
        FROM candles GROUP BY ticker, sector ORDER BY sector, ticker
    """).df()

db_stats = load_db_stats()

# ── Timeframe adattivo: meno candele su periodi lunghi = veloce ─
def choose_bucket(days: int):
    """Sceglie l'aggregazione in base al periodo. Restituisce (intervallo_sql, etichetta)."""
    if days <= 8:    return "15 minutes", "15 min"
    if days <= 31:   return "1 hour",     "1 ora"
    if days <= 130:  return "4 hours",    "4 ore"
    if days <= 800:  return "1 day",      "giornaliere"
    return "1 week", "settimanali"


# ── Carica candele aggregate + ricalcola indicatori sul timeframe ─
def load_candles(ticker: str, days: int = 90):
    bucket_sql, label = choose_bucket(days)

    df = conn.execute(f"""
        SELECT time_bucket(INTERVAL '{bucket_sql}', ts) AS ts,
               arg_min(open, ts)  AS open,
               max(high)          AS high,
               min(low)           AS low,
               arg_max(close, ts) AS close,
               sum(volume)        AS volume
        FROM candles
        WHERE ticker = ?
          AND ts >= (SELECT MAX(ts) FROM candles WHERE ticker = ?) - INTERVAL (?) DAY
        GROUP BY 1
        ORDER BY 1
    """, [ticker, ticker, days]).df()

    if df.empty:
        return df, label

    # Ricalcola indicatori sul timeframe mostrato (corretto per la vista)
    df = add_indicators(df)
    for c in ["rsi", "macd", "macd_signal", "macd_hist",
              "ema_20", "ema_50", "ema_200", "bb_upper", "bb_mid", "bb_lower", "atr"]:
        if c not in df.columns:
            df[c] = float("nan")
    return df, label

# ── Carica heatmap performance ultimi N giorni ───────────────
def load_heatmap(days: int = 5) -> pd.DataFrame:
    return conn.execute("""
        WITH ranked AS (
            SELECT ticker, sector, close, ts,
                   ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY ts ASC)  AS rn_first,
                   ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY ts DESC) AS rn_last,
                   COUNT(*) OVER (PARTITION BY ticker) AS total
            FROM candles
            WHERE ts >= (SELECT MAX(ts) FROM candles) - INTERVAL (?) DAY
        ),
        first_last AS (
            SELECT ticker, sector,
                   MAX(CASE WHEN rn_first = 1 THEN close END) AS first_close,
                   MAX(CASE WHEN rn_last  = 1 THEN close END) AS last_close
            FROM ranked GROUP BY ticker, sector
        )
        SELECT ticker, sector,
               ROUND((last_close - first_close) / first_close * 100, 2) AS perf_pct
        FROM first_last
        ORDER BY sector, ticker
    """, [days]).df()

# ── Grafico candlestick principale ──────────────────────────
def make_chart(ticker: str, days: int, show_ema: bool, show_bb: bool) -> go.Figure:
    df, label = load_candles(ticker, days)
    if df.empty:
        return go.Figure()

    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=[0.54, 0.13, 0.165, 0.165],
        subplot_titles=[
            f"Prezzo · candele {label}",
            "Volume",
            "RSI (0–100)",
            "MACD",
        ]
    )

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df["ts"], open=df["open"], high=df["high"],
        low=df["low"], close=df["close"],
        name="Prezzo",
        increasing_line_color="#22c55e",
        decreasing_line_color="#ef4444",
        increasing_fillcolor="#22c55e",
        decreasing_fillcolor="#ef4444",
    ), row=1, col=1)

    # EMAs
    if show_ema:
        for period, color in [(20, "#facc15"), (50, "#fb923c"), (200, "#818cf8")]:
            col = f"ema_{period}"
            if col in df.columns and df[col].notna().any():
                fig.add_trace(go.Scatter(
                    x=df["ts"], y=df[col],
                    name=f"EMA {period}", line=dict(color=color, width=1.2),
                    hovertemplate=f"EMA{period}: %{{y:.2f}}<extra></extra>"
                ), row=1, col=1)

    # Bollinger Bands
    if show_bb and df["bb_upper"].notna().any():
        fig.add_trace(go.Scatter(
            x=df["ts"], y=df["bb_upper"], name="BB Upper",
            line=dict(color="#94a3b8", width=1, dash="dot"),
            hovertemplate="BB Upper: %{y:.2f}<extra></extra>"
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df["ts"], y=df["bb_lower"], name="BB Lower",
            line=dict(color="#94a3b8", width=1, dash="dot"),
            fill="tonexty", fillcolor="rgba(148,163,184,0.08)",
            hovertemplate="BB Lower: %{y:.2f}<extra></extra>"
        ), row=1, col=1)

    # Volume (riga dedicata — non schiaccia più le candele)
    colors = ["#22c55e" if c >= o else "#ef4444"
              for c, o in zip(df["close"], df["open"])]
    fig.add_trace(go.Bar(
        x=df["ts"], y=df["volume"], name="Volume",
        marker_color=colors, opacity=0.6,
        hovertemplate="Volume: %{y:,.0f}<extra></extra>",
        showlegend=False,
    ), row=2, col=1)

    # RSI
    fig.add_trace(go.Scatter(
        x=df["ts"], y=df["rsi"], name="RSI",
        line=dict(color="#a78bfa", width=1.5),
        hovertemplate="RSI: %{y:.1f}<extra></extra>",
        showlegend=False,
    ), row=3, col=1)
    fig.add_hline(y=70, line_dash="dot", line_color="rgba(239,68,68,0.5)", row=3, col=1)
    fig.add_hline(y=30, line_dash="dot", line_color="rgba(34,197,94,0.5)",  row=3, col=1)
    fig.add_hrect(y0=70, y1=100, fillcolor="rgba(239,68,68,0.06)", line_width=0, row=3, col=1)
    fig.add_hrect(y0=0,  y1=30,  fillcolor="rgba(34,197,94,0.06)",  line_width=0, row=3, col=1)

    # MACD
    if df["macd"].notna().any():
        fig.add_trace(go.Scatter(
            x=df["ts"], y=df["macd"], name="MACD",
            line=dict(color="#38bdf8", width=1.5)
        ), row=4, col=1)
        fig.add_trace(go.Scatter(
            x=df["ts"], y=df["macd_signal"], name="Signal",
            line=dict(color="#f97316", width=1.5)
        ), row=4, col=1)
        hist_colors = ["#22c55e" if v >= 0 else "#ef4444"
                       for v in df["macd_hist"].fillna(0)]
        fig.add_trace(go.Bar(
            x=df["ts"], y=df["macd_hist"], name="Hist",
            marker_color=hist_colors, opacity=0.6, showlegend=False,
        ), row=4, col=1)

    # Riepilogo prezzo nel titolo
    sector = TICKER_TO_SECTOR.get(ticker, "")
    last  = float(df["close"].iloc[-1])
    first = float(df["open"].iloc[0])
    chg   = (last / first - 1) * 100 if first else 0
    chg_color = "#22c55e" if chg >= 0 else "#ef4444"
    arrow = "▲" if chg >= 0 else "▼"
    title = (
        f"{ticker}  "
        f"<span style='color:#e2e8f0;font-size:16px'>${last:,.2f}</span>  "
        f"<span style='color:{chg_color};font-size:14px'>{arrow} {chg:+.1f}%</span>"
        f"<span style='color:#64748b;font-size:12px'>  ·  {sector}  ·  candele {label}</span>"
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0f172a",
        plot_bgcolor="#0f172a",
        font=dict(family="Inter, sans-serif", color="#e2e8f0"),
        height=820,
        margin=dict(l=10, r=10, t=60, b=10),
        legend=dict(orientation="h", y=1.02, x=0,
                    bgcolor="rgba(0,0,0,0)", font_size=11),
        xaxis_rangeslider_visible=False,
        hovermode="x unified",
        bargap=0,
        uirevision=ticker,   # mantiene lo zoom quando cambi indicatori
        title=dict(text=title, font_size=18, x=0.01),
    )
    fig.update_yaxes(gridcolor="#1e293b", zerolinecolor="#334155")
    fig.update_xaxes(gridcolor="#1e293b", showspikes=True, spikecolor="#475569")
    # Nasconde i buchi del weekend così la linea è continua
    fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])])
    return fig

# ── Heatmap settoriale ───────────────────────────────────────
def make_heatmap(days: int) -> go.Figure:
    df = load_heatmap(days)
    if df.empty:
        return go.Figure()

    sectors = list(TICKERS_BY_SECTOR.keys())
    max_tickers = max(len(v) for v in TICKERS_BY_SECTOR.values())

    z, text, customdata = [], [], []
    y_labels = []

    for sector in sectors:
        row_z, row_text, row_custom = [], [], []
        tickers_in_sector = TICKERS_BY_SECTOR[sector]
        sector_df = df[df["sector"] == sector].set_index("ticker")

        for ticker in tickers_in_sector:
            perf = float(sector_df.loc[ticker, "perf_pct"]) if ticker in sector_df.index else 0.0
            row_z.append(perf)
            sign = "+" if perf >= 0 else ""
            row_text.append(f"{ticker}<br>{sign}{perf:.1f}%")
            row_custom.append(ticker)

        while len(row_z) < max_tickers:
            row_z.append(None)
            row_text.append("")
            row_custom.append("")

        z.append(row_z)
        text.append(row_text)
        customdata.append(row_custom)
        y_labels.append(sector)

    fig = go.Figure(go.Heatmap(
        z=z, text=text, customdata=customdata,
        texttemplate="%{text}",
        colorscale=[
            [0.0,  "#7f1d1d"],
            [0.25, "#ef4444"],
            [0.45, "#fca5a5"],
            [0.50, "#1e293b"],
            [0.55, "#86efac"],
            [0.75, "#22c55e"],
            [1.0,  "#14532d"],
        ],
        zmid=0,
        showscale=True,
        colorbar=dict(title="% change", ticksuffix="%", thickness=12),
        hovertemplate="%{customdata}<br>Performance: %{z:.2f}%<extra></extra>",
        xgap=3, ygap=3,
    ))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0f172a",
        plot_bgcolor="#0f172a",
        font=dict(color="#e2e8f0"),
        height=540,
        margin=dict(l=10, r=60, t=40, b=10),
        yaxis=dict(tickvals=list(range(len(y_labels))), ticktext=y_labels, tickfont_size=11),
        xaxis=dict(showticklabels=False),
        title=dict(text=f"Heatmap settoriale — ultimi {days} giorni", font_size=15, x=0.01)
    )
    return fig

# ── Crescita settori nel tempo ───────────────────────────────
def load_sector_growth(days: int) -> pd.DataFrame:
    """Chiusura giornaliera (ultima candela del giorno) per ogni ticker."""
    return conn.execute("""
        SELECT date, ticker, sector, close FROM (
            SELECT ts::DATE AS date, ticker, sector, close,
                   ROW_NUMBER() OVER (PARTITION BY ticker, ts::DATE ORDER BY ts DESC) AS rn
            FROM candles
            WHERE ts >= (SELECT MAX(ts) FROM candles) - INTERVAL (?) DAY
        ) WHERE rn = 1
        ORDER BY date
    """, [days]).df()


def make_sector_growth(days: int) -> go.Figure:
    df = load_sector_growth(days)
    if df.empty:
        return go.Figure()

    # Pivot: una colonna per ticker, indice = data
    pivot = df.pivot_table(index="date", columns="ticker", values="close").ffill()

    # Normalizza ogni ticker al suo primo valore valido = 100
    first_valid = pivot.apply(lambda c: c[c.first_valid_index()])
    normalized = pivot.divide(first_valid, axis=1) * 100

    fig = go.Figure()
    for sector, tickers in TICKERS_BY_SECTOR.items():
        cols = [t for t in tickers if t in normalized.columns]
        if not cols:
            continue
        # Indice settoriale = media equipesata dei titoli del settore
        sector_index = normalized[cols].mean(axis=1)
        growth = sector_index - 100  # crescita % dall'inizio del periodo

        fig.add_trace(go.Scatter(
            x=growth.index, y=growth.values,
            name=sector,
            line=dict(color=SECTOR_COLORS.get(sector, "#94a3b8"), width=2),
            hovertemplate=f"<b>{sector}</b><br>%{{x|%d %b %Y}}<br>%{{y:+.1f}}%<extra></extra>",
        ))

    fig.add_hline(y=0, line_dash="dot", line_color="#475569")

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0f172a",
        plot_bgcolor="#0f172a",
        font=dict(family="Inter, sans-serif", color="#e2e8f0"),
        height=600,
        margin=dict(l=10, r=10, t=50, b=10),
        hovermode="x unified",
        legend=dict(font_size=11, bgcolor="rgba(15,23,42,0.6)"),
        title=dict(text="Crescita dei settori — % dall'inizio del periodo", font_size=15, x=0.01),
    )
    fig.update_yaxes(gridcolor="#1e293b", zerolinecolor="#334155", ticksuffix="%")
    fig.update_xaxes(gridcolor="#1e293b", showspikes=True, spikecolor="#475569")
    return fig


# ── Tabella stato DB ─────────────────────────────────────────
def make_db_table() -> list:
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
            html.Td(str(row["dal"]), style={"padding": "4px 12px", "color": "#94a3b8"}),
            html.Td(str(row["al"]),  style={"padding": "4px 12px", "color": "#94a3b8"}),
        ], style={"borderBottom": "1px solid #1e293b"}))
    return rows

# ── Card descrittiva per il pannello spiegazioni ─────────────
def _info_card(icon: str, titolo: str, colore: str, testo: str):
    return html.Div([
        html.Div([
            html.Span(icon, style={"fontSize": "18px", "marginRight": "8px"}),
            html.Span(titolo, style={"color": colore, "fontWeight": "600", "fontSize": "14px"}),
        ], className="mb-1"),
        html.Small(testo, style={"color": "#94a3b8", "fontSize": "12px", "lineHeight": "1.4"}),
    ], style={"backgroundColor": "#0f172a", "border": "1px solid #1e293b",
              "borderRadius": "8px", "padding": "12px", "height": "100%"})


# ── Layout ───────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.CYBORG],
    title="AI Market Predictor",
)

TICKER_OPTIONS = [
    {"label": f"{t}  ({TICKER_TO_SECTOR.get(t, '')})", "value": t}
    for t in ALL_TICKERS
]

app.layout = dbc.Container([

    dbc.Row([
        dbc.Col([
            html.H4("AI Market Predictor",
                    className="mb-0", style={"color": "#818cf8", "fontWeight": "700"}),
            html.Small("Dashboard — Fase 1 · Passo 4", style={"color": "#64748b"}),
        ], width=6),
        dbc.Col([
            html.Div([
                html.Span(f"{db_stats['n'].sum():,} candele",
                          style={"color": "#22c55e", "marginRight": "16px", "fontWeight": "600"}),
                html.Span(f"{db_stats['ticker'].nunique()} ticker · 11 settori",
                          style={"color": "#94a3b8"}),
            ], className="text-end mt-2")
        ], width=6),
    ], className="py-3 border-bottom border-secondary mb-3"),

    dbc.Tabs([

        # ── Tab Grafico ──────────────────────────────────────
        dbc.Tab(label="📈  Grafico", tab_id="chart", children=[
            dbc.Row([
                dbc.Col([
                    dbc.Label("Ticker", style={"fontSize": "12px", "color": "#94a3b8"}),
                    dcc.Dropdown(id="ticker-select", options=TICKER_OPTIONS,
                                 value="AAPL", clearable=False),
                ], width=3),
                dbc.Col([
                    dbc.Label("Periodo", style={"fontSize": "12px", "color": "#94a3b8"}),
                    dcc.Dropdown(id="period-select", value=365, clearable=False, options=[
                        {"label": "1 settimana  (15 min)",  "value": 7},
                        {"label": "1 mese  (1 ora)",        "value": 30},
                        {"label": "3 mesi  (4 ore)",        "value": 90},
                        {"label": "6 mesi  (giornaliere)",  "value": 180},
                        {"label": "1 anno  (giornaliere)",  "value": 365},
                        {"label": "2 anni  (giornaliere)",  "value": 730},
                        {"label": "5 anni  (settimanali)",  "value": 1825},
                    ]),
                ], width=3),
                dbc.Col([
                    dbc.Label("Overlay", style={"fontSize": "12px", "color": "#94a3b8"}),
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
            ], className="mt-3 mb-2 g-3"),

            # Pannello spiegazioni — espandibile
            dbc.Accordion([
                dbc.AccordionItem([
                    dbc.Row([
                        dbc.Col(_info_card("🕯️", "Candele 15 min", "#22c55e",
                            "Ogni candela = 15 minuti di mercato. Verde = il prezzo è salito, "
                            "rossa = sceso. Il corpo va da apertura a chiusura; le linee sottili "
                            "(stoppini) sono il massimo e minimo toccati."), md=6, lg=4),
                        dbc.Col(_info_card("📊", "Volume", "#64748b",
                            "Quante azioni sono state scambiate in quei 15 minuti. Volume alto "
                            "= movimento affidabile e partecipato. Volume basso = movimento debole."), md=6, lg=4),
                        dbc.Col(_info_card("📈", "EMA 20 / 50 / 200", "#facc15",
                            "Medie mobili dei prezzi su breve (20), medio (50) e lungo periodo (200). "
                            "Prezzo sopra le linee = tendenza rialzista. La EMA 200 è il trend di fondo."), md=6, lg=4),
                        dbc.Col(_info_card("🎯", "Bollinger Bands", "#94a3b8",
                            "Banda di volatilità intorno al prezzo. Prezzo vicino alla banda alta "
                            "= forse troppo caro (ipercomprato); vicino alla bassa = forse a sconto "
                            "(ipervenduto)."), md=6, lg=4),
                        dbc.Col(_info_card("⚡", "RSI (0-100)", "#a78bfa",
                            "Misura la forza del movimento. Sopra 70 (zona rossa) = ipercomprato, "
                            "possibile calo. Sotto 30 (zona verde) = ipervenduto, possibile rimbalzo."), md=6, lg=4),
                        dbc.Col(_info_card("🔄", "MACD", "#38bdf8",
                            "Segnala i cambi di tendenza. Quando la linea blu incrocia l'arancione "
                            "verso l'alto = momentum rialzista; verso il basso = ribassista. "
                            "Le barre mostrano la forza del segnale."), md=6, lg=4),
                    ], className="g-2"),
                ], title="ℹ️  Cosa sto guardando? — clicca per la spiegazione"),
            ], start_collapsed=True, className="mb-3"),

            dcc.Loading(
                dcc.Graph(id="main-chart", config={"scrollZoom": True}),
                type="circle", color="#818cf8",
            ),
        ]),

        # ── Tab Heatmap ──────────────────────────────────────
        dbc.Tab(label="🟩  Heatmap settoriale", tab_id="heatmap", children=[
            html.P("Tutti i 66 titoli colorati in base alla performance del periodo scelto. "
                   "Verde = il prezzo è salito, rosso = sceso. Ogni riga è un settore: "
                   "serve a vedere a colpo d'occhio quali settori si muovono insieme.",
                   style={"color": "#94a3b8", "fontSize": "13px", "marginTop": "16px"}),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Periodo", style={"fontSize": "12px", "color": "#94a3b8"}),
                    dcc.Dropdown(id="heatmap-period", value=5, clearable=False,
                                 style={"width": "200px"}, options=[
                        {"label": "Oggi",      "value": 1},
                        {"label": "5 giorni",  "value": 5},
                        {"label": "1 mese",    "value": 30},
                        {"label": "3 mesi",    "value": 90},
                        {"label": "6 mesi",    "value": 180},
                        {"label": "1 anno",    "value": 365},
                    ]),
                ], width=3),
            ], className="mt-3 mb-2"),
            dcc.Loading(
                dcc.Graph(id="heatmap-chart"),
                type="circle", color="#818cf8",
            ),
        ]),

        # ── Tab Crescita settori ─────────────────────────────
        dbc.Tab(label="📊  Settori nel tempo", tab_id="growth", children=[
            html.P("Come è cresciuto ogni settore nel tempo. Ogni linea parte da 0% "
                   "all'inizio del periodo: così confronti chi è salito di più e chi di meno. "
                   "Clicca un settore nella legenda per nasconderlo o isolarlo.",
                   style={"color": "#94a3b8", "fontSize": "13px", "marginTop": "16px"}),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Periodo", style={"fontSize": "12px", "color": "#94a3b8"}),
                    dcc.Dropdown(id="growth-period", value=730, clearable=False,
                                 style={"width": "200px"}, options=[
                        {"label": "6 mesi",  "value": 180},
                        {"label": "1 anno",  "value": 365},
                        {"label": "2 anni",  "value": 730},
                        {"label": "3 anni",  "value": 1095},
                        {"label": "Tutto",   "value": 3000},
                    ]),
                ], width=3),
            ], className="mt-2 mb-2"),
            dcc.Loading(
                dcc.Graph(id="growth-chart"),
                type="circle", color="#818cf8",
            ),
        ]),

        # ── Tab Database ─────────────────────────────────────
        dbc.Tab(label="💾  Database", tab_id="db", children=[
            html.P("Lo stato dei dati scaricati: quante candele abbiamo per ogni titolo "
                   "e il periodo coperto. Serve a verificare che il database sia completo "
                   "prima di addestrare il modello.",
                   style={"color": "#94a3b8", "fontSize": "13px", "marginTop": "16px"}),
            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H3(f"{db_stats['n'].sum():,}",
                            style={"color": "#818cf8", "margin": "0"}),
                    html.Small("Candele totali", style={"color": "#94a3b8"}),
                ])), width=3),
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H3(str(db_stats["ticker"].nunique()),
                            style={"color": "#22c55e", "margin": "0"}),
                    html.Small("Ticker", style={"color": "#94a3b8"}),
                ])), width=3),
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H3(str(db_stats["dal"].min()),
                            style={"color": "#f59e0b", "margin": "0"}),
                    html.Small("Primo dato", style={"color": "#94a3b8"}),
                ])), width=3),
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H3(str(db_stats["al"].max()),
                            style={"color": "#f59e0b", "margin": "0"}),
                    html.Small("Ultimo dato", style={"color": "#94a3b8"}),
                ])), width=3),
            ], className="mt-3 mb-3 g-2"),

            html.Div([
                html.Table([
                    html.Thead(html.Tr([
                        html.Th("Ticker",   style={"padding": "8px 12px"}),
                        html.Th("Candele",  style={"padding": "8px 12px", "textAlign": "right"}),
                        html.Th("Dal",      style={"padding": "8px 12px"}),
                        html.Th("Al",       style={"padding": "8px 12px"}),
                    ]), style={"backgroundColor": "#1e293b", "fontSize": "12px",
                               "color": "#94a3b8", "textTransform": "uppercase",
                               "position": "sticky", "top": "0"}),
                    html.Tbody(make_db_table(), style={"fontSize": "13px"}),
                ], style={"width": "100%", "borderCollapse": "collapse"}),
            ], style={"maxHeight": "520px", "overflowY": "auto",
                      "backgroundColor": "#0f172a", "borderRadius": "8px",
                      "border": "1px solid #1e293b"}),
        ]),

    ], id="tabs", active_tab="chart"),

], fluid=True, style={"backgroundColor": "#0a0f1e", "minHeight": "100vh",
                       "fontFamily": "Inter, system-ui, sans-serif"})


# ── Callbacks ────────────────────────────────────────────────
@callback(
    Output("main-chart", "figure"),
    Input("ticker-select", "value"),
    Input("period-select", "value"),
    Input("indicator-select", "value"),
)
def update_chart(ticker, days, indicators):
    show_ema = "ema" in (indicators or [])
    show_bb  = "bb"  in (indicators or [])
    return make_chart(ticker, days, show_ema, show_bb)


@callback(
    Output("heatmap-chart", "figure"),
    Input("heatmap-period", "value"),
)
def update_heatmap(days):
    return make_heatmap(days)


@callback(
    Output("growth-chart", "figure"),
    Input("growth-period", "value"),
)
def update_growth(days):
    return make_sector_growth(days)


if __name__ == "__main__":
    print()
    print("  ╔══════════════════════════════════════╗")
    print("  ║   AI Market Predictor — Dashboard    ║")
    print("  ║   http://127.0.0.1:8050              ║")
    print("  ╚══════════════════════════════════════╝")
    print()
    app.run(debug=False, port=8050)
