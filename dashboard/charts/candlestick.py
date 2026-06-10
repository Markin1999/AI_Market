"""
Grafico a candele — il grafico principale della dashboard.

Composto da 4 riquadri verticali allineati sullo stesso asse temporale:
    1. Prezzo   — candele giapponesi + overlay opzionali (EMA, Bollinger)
    2. Volume   — barre verdi/rosse
    3. RSI      — oscillatore 0-100 con zone di iper-comprato/venduto
    4. MACD     — linee MACD/Signal + istogramma

I dati arrivano già aggregati e con indicatori da `data/candles.py`.
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from shared.config.settings import TICKER_TO_SECTOR
from dashboard.data.candles import load_candles
from dashboard.charts.theme import base_layout, GREEN, RED, GRID, ZEROLINE, SPIKE, TEXT


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
        ],
    )

    # ── 1. Candlestick ────────────────────────────────────────────────────────
    fig.add_trace(go.Candlestick(
        x=df["ts"], open=df["open"], high=df["high"],
        low=df["low"], close=df["close"],
        name="Prezzo",
        increasing_line_color=GREEN, decreasing_line_color=RED,
        increasing_fillcolor=GREEN, decreasing_fillcolor=RED,
    ), row=1, col=1)

    # EMA 20 / 50 / 200
    if show_ema:
        for period, color in [(20, "#facc15"), (50, "#fb923c"), (200, "#818cf8")]:
            col = f"ema_{period}"
            if col in df.columns and df[col].notna().any():
                fig.add_trace(go.Scatter(
                    x=df["ts"], y=df[col],
                    name=f"EMA {period}", line=dict(color=color, width=1.2),
                    hovertemplate=f"EMA{period}: %{{y:.2f}}<extra></extra>",
                ), row=1, col=1)

    # Bollinger Bands
    if show_bb and df["bb_upper"].notna().any():
        fig.add_trace(go.Scatter(
            x=df["ts"], y=df["bb_upper"], name="BB Upper",
            line=dict(color="#94a3b8", width=1, dash="dot"),
            hovertemplate="BB Upper: %{y:.2f}<extra></extra>",
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df["ts"], y=df["bb_lower"], name="BB Lower",
            line=dict(color="#94a3b8", width=1, dash="dot"),
            fill="tonexty", fillcolor="rgba(148,163,184,0.08)",
            hovertemplate="BB Lower: %{y:.2f}<extra></extra>",
        ), row=1, col=1)

    # ── 2. Volume ─────────────────────────────────────────────────────────────
    colors = [GREEN if c >= o else RED for c, o in zip(df["close"], df["open"])]
    fig.add_trace(go.Bar(
        x=df["ts"], y=df["volume"], name="Volume",
        marker_color=colors, opacity=0.6,
        hovertemplate="Volume: %{y:,.0f}<extra></extra>",
        showlegend=False,
    ), row=2, col=1)

    # ── 3. RSI ────────────────────────────────────────────────────────────────
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

    # ── 4. MACD ───────────────────────────────────────────────────────────────
    if df["macd"].notna().any():
        fig.add_trace(go.Scatter(
            x=df["ts"], y=df["macd"], name="MACD",
            line=dict(color="#38bdf8", width=1.5),
        ), row=4, col=1)
        fig.add_trace(go.Scatter(
            x=df["ts"], y=df["macd_signal"], name="Signal",
            line=dict(color="#f97316", width=1.5),
        ), row=4, col=1)
        hist_colors = [GREEN if v >= 0 else RED for v in df["macd_hist"].fillna(0)]
        fig.add_trace(go.Bar(
            x=df["ts"], y=df["macd_hist"], name="Hist",
            marker_color=hist_colors, opacity=0.6, showlegend=False,
        ), row=4, col=1)

    # ── Titolo con prezzo e variazione ────────────────────────────────────────
    sector = TICKER_TO_SECTOR.get(ticker, "")
    last  = float(df["close"].iloc[-1])
    first = float(df["open"].iloc[0])
    chg   = (last / first - 1) * 100 if first else 0
    chg_color = GREEN if chg >= 0 else RED
    arrow = "▲" if chg >= 0 else "▼"
    title = (
        f"{ticker}  "
        f"<span style='color:{TEXT};font-size:16px'>${last:,.2f}</span>  "
        f"<span style='color:{chg_color};font-size:14px'>{arrow} {chg:+.1f}%</span>"
        f"<span style='color:#64748b;font-size:12px'>  ·  {sector}  ·  candele {label}</span>"
    )

    fig.update_layout(**base_layout(
        height=820,
        margin=dict(l=10, r=10, t=60, b=10),
        legend=dict(orientation="h", y=1.02, x=0,
                    bgcolor="rgba(0,0,0,0)", font_size=11),
        xaxis_rangeslider_visible=False,
        hovermode="x unified",
        bargap=0,
        uirevision=ticker,   # mantiene lo zoom quando cambi gli overlay
        title=dict(text=title, font_size=18, x=0.01),
    ))
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=ZEROLINE)
    fig.update_xaxes(gridcolor=GRID, showspikes=True, spikecolor=SPIKE)
    # Nasconde i buchi del weekend così la linea resta continua
    fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])])
    return fig
