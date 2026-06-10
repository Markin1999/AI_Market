"""
Indicatore per settore — confronto di un indicatore tra i titoli di un settore.

Scegli un indicatore (es. RSI) e un settore (es. Technology): vedi la stessa
misura disegnata per ogni titolo del settore, così confronti chi è ipercomprato,
chi ipervenduto, chi sta accelerando. Ha senso solo per indicatori confrontabili
tra titoli (oscillatori normalizzati): il catalogo li marca con `comparable=True`.
"""
import plotly.graph_objects as go

from shared.config.settings import TICKERS_BY_SECTOR
from dashboard.data.indicators import load_sector_indicator
from dashboard.indicators.catalog import CATALOG
from dashboard.charts.theme import base_layout, GRID, ZEROLINE, SPIKE

_LINE_COLORS = [
    "#38bdf8", "#f97316", "#a78bfa", "#34d399", "#fb7185", "#facc15",
    "#22d3ee", "#f472b6", "#a3e635", "#fbbf24", "#818cf8", "#2dd4bf",
]


def make_sector_indicator(indicator_key: str, sector: str, days: int) -> go.Figure:
    ind = CATALOG.get(indicator_key)
    if ind is None or sector not in TICKERS_BY_SECTOR:
        return go.Figure()

    tickers = TICKERS_BY_SECTOR[sector]
    df, label = load_sector_indicator(ind.primary, tickers, days)
    if df.empty:
        return go.Figure()

    fig = go.Figure()
    for i, t in enumerate(tickers):
        sub = df[df["ticker"] == t]
        if sub.empty:
            continue
        fig.add_trace(go.Scatter(
            x=sub["ts"], y=sub["value"], name=t,
            line=dict(width=1.6, color=_LINE_COLORS[i % len(_LINE_COLORS)]),
            hovertemplate=f"<b>{t}</b>  %{{y:.1f}}<extra></extra>",
        ))

    # Linee guida secondo la scala dell'indicatore
    if ind.unit == "0–100":
        fig.add_hline(y=70, line_dash="dot", line_color="rgba(239,68,68,0.4)")
        fig.add_hline(y=30, line_dash="dot", line_color="rgba(34,197,94,0.4)")
    elif ind.unit == "-100–0":
        fig.add_hline(y=-20, line_dash="dot", line_color="rgba(239,68,68,0.4)")
        fig.add_hline(y=-80, line_dash="dot", line_color="rgba(34,197,94,0.4)")
    elif ind.unit in ("±", "±%", "-1–+1"):
        fig.add_hline(y=0, line_dash="dot", line_color=ZEROLINE)

    fig.update_layout(**base_layout(
        height=600,
        hovermode="x unified",
        legend=dict(font_size=11, bgcolor="rgba(15,23,42,0.6)"),
        title=dict(text=f"{ind.name} — settore {sector}  ·  candele {label}",
                   font_size=15, x=0.01),
    ))
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=ZEROLINE)
    fig.update_xaxes(gridcolor=GRID, showspikes=True, spikecolor=SPIKE,
                     rangebreaks=[dict(bounds=["sat", "mon"])])
    return fig
