"""
Mostra COSA fa il Passo 2, in modo visivo.

Prende un giorno reale di un titolo (una "finestra" da 64 candele) e lo disegna
in due modi:
  1) come lo vedi TU      → le candele reali
  2) come lo riceve l'OCCHIO → normalizzato (stessa forma, numeri confrontabili)

Crea un file HTML da aprire nel browser:
    python training/occhio/mostra_finestra.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import numpy as np
import duckdb
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from training import config
from training.data.windows import load_clean_series, _SOURCE_COLS
from training.data.normalize import Normalizer

TICKER = "AAPL"
OUT = Path(__file__).resolve().parents[2] / "finestra_esempio.html"

conn = duckdb.connect(str(config.DB_PATH), read_only=True)
df = load_clean_series(conn, TICKER)
conn.close()

# Ultima finestra completa = un giorno
win = df.iloc[-config.WINDOW:].reset_index(drop=True)
arr = Normalizer(_SOURCE_COLS)(win[_SOURCE_COLS].to_numpy(np.float32))  # (64 candele, 47 numeri)
norm_close = arr[:, config.FEATURE_COLS.index("close")]
giorno = str(win["ts"].iloc[0])[:10]

fig = make_subplots(
    rows=2, cols=1, vertical_spacing=0.14,
    subplot_titles=[
        f"1) Quello che vedi TU — {TICKER} il {giorno}  (un giorno = {config.WINDOW} candele da 15 min)",
        "2) Quello che riceve l'OCCHIO — stessa forma, numeri normalizzati e confrontabili tra titoli",
    ],
)
fig.add_trace(go.Candlestick(
    x=list(range(len(win))),
    open=win["open"], high=win["high"], low=win["low"], close=win["close"],
    increasing_line_color="#22c55e", decreasing_line_color="#ef4444",
), row=1, col=1)
fig.add_trace(go.Scatter(
    y=norm_close, mode="lines+markers",
    line=dict(color="#818cf8", width=2), marker=dict(size=3),
), row=2, col=1)

fig.update_layout(
    template="plotly_dark", height=720, showlegend=False,
    xaxis_rangeslider_visible=False,
    title=dict(text="UNA finestra = un giorno. L'occhio ne studierà MILIONI "
                    "(tutti i titoli, tutti gli anni).", x=0.5),
)
fig.write_html(str(OUT), include_plotlyjs=True)
print("✓ Immagine creata:", OUT.name)
