"""
Heatmap settoriale — tutti i 66 titoli colorati per performance.

Ogni riga è un settore, ogni cella un titolo. Verde = salito, rosso = sceso
nel periodo scelto. Serve a vedere a colpo d'occhio quali settori si muovono
insieme. I dati arrivano da `data/heatmap.py`.
"""
import plotly.graph_objects as go

from shared.config.settings import TICKERS_BY_SECTOR
from dashboard.data.heatmap import load_heatmap
from dashboard.charts.theme import base_layout


def make_heatmap(days: int) -> go.Figure:
    df = load_heatmap(days)
    if df.empty:
        return go.Figure()

    sectors = list(TICKERS_BY_SECTOR.keys())
    max_tickers = max(len(v) for v in TICKERS_BY_SECTOR.values())

    z, text, customdata, y_labels = [], [], [], []

    for sector in sectors:
        row_z, row_text, row_custom = [], [], []
        sector_df = df[df["sector"] == sector].set_index("ticker")

        for ticker in TICKERS_BY_SECTOR[sector]:
            perf = float(sector_df.loc[ticker, "perf_pct"]) if ticker in sector_df.index else 0.0
            row_z.append(perf)
            sign = "+" if perf >= 0 else ""
            row_text.append(f"{ticker}<br>{sign}{perf:.1f}%")
            row_custom.append(ticker)

        # Pad delle righe più corte così la griglia resta rettangolare
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

    fig.update_layout(**base_layout(
        height=540,
        margin=dict(l=10, r=60, t=40, b=10),
        yaxis=dict(tickvals=list(range(len(y_labels))), ticktext=y_labels, tickfont_size=11),
        xaxis=dict(showticklabels=False),
        title=dict(text=f"Heatmap settoriale — ultimi {days} giorni", font_size=15, x=0.01),
    ))
    return fig
