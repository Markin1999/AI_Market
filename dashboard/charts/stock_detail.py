"""
Pagina azione — grafico componibile con tutti gli indicatori del titolo.

L'utente sceglie un titolo e quali indicatori aggiungere. Il grafico si
costruisce da solo:
    • il prezzo a candele è sempre il primo pannello
    • gli indicatori "overlay" (EMA, Bollinger, PSAR, Donchian, Keltner,
      Ichimoku) si disegnano SOPRA il prezzo
    • i pattern candele appaiono come frecce verdi/rosse sul prezzo
    • ogni altro indicatore (RSI, MACD, ADX, ...) prende un pannello tutto suo

I dati sono i valori MEMORIZZATI nel database (vedi data/indicators.py).
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from dashboard.data.indicators import load_stock_full
from dashboard.indicators.catalog import CATALOG
from dashboard.charts.theme import base_layout, GREEN, RED, GRID, ZEROLINE, SPIKE, TEXT

# Colori ciclici per le linee
_OVERLAY_COLORS = ["#facc15", "#fb923c", "#818cf8", "#22d3ee", "#f472b6", "#a3e635"]
_PANEL_COLORS   = ["#38bdf8", "#f97316", "#a78bfa", "#34d399", "#fb7185", "#facc15"]


def _guides(fig, unit: str, row: int):
    """Aggiunge le linee guida adatte alla scala dell'indicatore."""
    if unit == "0–100":
        fig.add_hline(y=70, line_dash="dot", line_color="rgba(239,68,68,0.4)", row=row, col=1)
        fig.add_hline(y=30, line_dash="dot", line_color="rgba(34,197,94,0.4)", row=row, col=1)
    elif unit == "-100–0":
        fig.add_hline(y=-20, line_dash="dot", line_color="rgba(239,68,68,0.4)", row=row, col=1)
        fig.add_hline(y=-80, line_dash="dot", line_color="rgba(34,197,94,0.4)", row=row, col=1)
    elif unit in ("±", "±%", "-1–+1"):
        fig.add_hline(y=0, line_dash="dot", line_color=ZEROLINE, row=row, col=1)


def make_stock_detail(ticker: str, days: int, selected_keys: list) -> go.Figure:
    entries = [CATALOG[k] for k in (selected_keys or []) if k in CATALOG]
    df, label = load_stock_full(ticker, days)
    if df.empty:
        return go.Figure()

    overlays = [e for e in entries if e.overlay and not e.pattern]
    patterns = [e for e in entries if e.pattern]
    panels   = [e for e in entries if not e.overlay and not e.pattern]

    rows = 1 + len(panels)
    weights = [3.0] + [1.0] * len(panels)
    total = sum(weights)
    row_heights = [w / total for w in weights]
    titles = ["Prezzo"] + [e.name for e in panels]

    fig = make_subplots(
        rows=rows, cols=1, shared_xaxes=True,
        vertical_spacing=0.03 if rows > 1 else 0.0,
        row_heights=row_heights, subplot_titles=titles,
    )

    # ── Pannello 1: prezzo a candele ──────────────────────────────────────────
    fig.add_trace(go.Candlestick(
        x=df["ts"], open=df["open"], high=df["high"], low=df["low"], close=df["close"],
        name="Prezzo",
        increasing_line_color=GREEN, decreasing_line_color=RED,
        increasing_fillcolor=GREEN, decreasing_fillcolor=RED,
    ), row=1, col=1)

    # Overlay (linee sul prezzo)
    ci = 0
    for e in overlays:
        for col in e.cols:
            if col in df.columns and df[col].notna().any():
                fig.add_trace(go.Scatter(
                    x=df["ts"], y=df[col], name=col,
                    line=dict(width=1.2, color=_OVERLAY_COLORS[ci % len(_OVERLAY_COLORS)]),
                ), row=1, col=1)
                ci += 1

    # Pattern candele (frecce)
    for e in patterns:
        col = e.cols[0]
        if col not in df.columns:
            continue
        bull = df[df[col] > 0]
        bear = df[df[col] < 0]
        if len(bull):
            fig.add_trace(go.Scatter(
                x=bull["ts"], y=bull["low"] * 0.998, mode="markers",
                name=f"{e.name} ▲",
                marker=dict(symbol="triangle-up", color=GREEN, size=9,
                            line=dict(width=0.5, color="#064e3b")),
                hovertemplate=f"{e.name} (rialzista)<extra></extra>",
            ), row=1, col=1)
        if len(bear):
            fig.add_trace(go.Scatter(
                x=bear["ts"], y=bear["high"] * 1.002, mode="markers",
                name=f"{e.name} ▼",
                marker=dict(symbol="triangle-down", color=RED, size=9,
                            line=dict(width=0.5, color="#7f1d1d")),
                hovertemplate=f"{e.name} (ribassista)<extra></extra>",
            ), row=1, col=1)

    # ── Pannelli successivi: un indicatore ciascuno ───────────────────────────
    for idx, e in enumerate(panels):
        r = 2 + idx
        pci = 0
        for col in e.cols:
            if col not in df.columns:
                continue
            if col.endswith("_hist"):
                colors = [GREEN if v >= 0 else RED for v in df[col].fillna(0)]
                fig.add_trace(go.Bar(
                    x=df["ts"], y=df[col], name=col,
                    marker_color=colors, opacity=0.5, showlegend=False,
                ), row=r, col=1)
            else:
                fig.add_trace(go.Scatter(
                    x=df["ts"], y=df[col], name=col,
                    line=dict(width=1.4, color=_PANEL_COLORS[pci % len(_PANEL_COLORS)]),
                ), row=r, col=1)
                pci += 1
        _guides(fig, e.unit, r)

    # ── Layout ────────────────────────────────────────────────────────────────
    n_ind = len(overlays) + len(patterns) + len(panels)
    height = 440 + 210 * len(panels)
    fig.update_layout(**base_layout(
        height=height,
        margin=dict(l=10, r=10, t=54, b=10),
        hovermode="x unified",
        xaxis_rangeslider_visible=False,
        bargap=0,
        uirevision=ticker,
        legend=dict(orientation="h", y=1.01, x=0, font_size=10, bgcolor="rgba(0,0,0,0)"),
        title=dict(
            text=f"<b style='color:{TEXT}'>{ticker}</b>  "
                 f"<span style='color:#64748b;font-size:12px'>candele {label} · {n_ind} indicatori</span>",
            font_size=16, x=0.01),
    ))
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=ZEROLINE)
    fig.update_xaxes(gridcolor=GRID, showspikes=True, spikecolor=SPIKE,
                     rangebreaks=[dict(bounds=["sat", "mon"])])
    return fig
