"""
Crescita dei settori nel tempo — confronto normalizzato.

Ogni settore è una linea che parte da 0% all'inizio del periodo. Così si
confronta chi è cresciuto di più indipendentemente dal prezzo assoluto.
L'indice di settore è la media equipesata dei suoi titoli.
I dati arrivano da `data/sectors.py`.
"""
import plotly.graph_objects as go

from shared.config.settings import TICKERS_BY_SECTOR
from dashboard.data.sectors import load_sector_growth
from dashboard.charts.theme import base_layout, SECTOR_COLORS, GRID, ZEROLINE, SPIKE


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

    fig.update_layout(**base_layout(
        height=600,
        hovermode="x unified",
        legend=dict(font_size=11, bgcolor="rgba(15,23,42,0.6)"),
        title=dict(text="Crescita dei settori — % dall'inizio del periodo", font_size=15, x=0.01),
    ))
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=ZEROLINE, ticksuffix="%")
    fig.update_xaxes(gridcolor=GRID, showspikes=True, spikecolor=SPIKE)
    return fig
