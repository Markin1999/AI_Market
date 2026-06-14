"""
Passo 3 — L'occhio all'opera: ORIGINALE vs COPIA.

Carica l'occhio addestrato, prende una finestra reale, gliela fa ridisegnare,
e disegna affianco l'originale e la copia (per il prezzo e per un indicatore).
Più le due linee si sovrappongono, meglio l'occhio "ci vede".

    python training/occhio/mostra_ricostruzione.py
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import numpy as np
import duckdb
import torch
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from training import config
from training.data.windows import load_clean_series, _SOURCE_COLS
from training.data.normalize import Normalizer
from training.occhio.architecture.vqvae import Autoencoder

TICKER = "AAPL"
MODEL = config.MODELS_DIR / "occhio_autoencoder.pt"
OUT = Path(__file__).resolve().parents[2] / "ricostruzione.html"

# Carica l'occhio addestrato
model = Autoencoder()
model.load_state_dict(torch.load(MODEL, map_location="cpu"))
model.eval()

# Una finestra reale (l'ultimo giorno completo del titolo)
conn = duckdb.connect(str(config.DB_PATH), read_only=True)
df = load_clean_series(conn, TICKER)
conn.close()

norm = Normalizer(_SOURCE_COLS)
arr = df[_SOURCE_COLS].to_numpy(np.float32)[-config.WINDOW:]
x = torch.from_numpy(norm(arr)).unsqueeze(0)        # (1, WINDOW, n_feature)
with torch.no_grad():
    recon = model(x)[0].numpy()
orig = x[0].numpy()

ci = config.FEATURE_COLS.index("close")
ri = config.FEATURE_COLS.index("rsi")

fig = make_subplots(
    rows=2, cols=1, vertical_spacing=0.15,
    subplot_titles=["Prezzo (la forma) — originale vs copia dell'occhio",
                    "RSI (un indicatore) — originale vs copia dell'occhio"],
)
fig.add_trace(go.Scatter(y=orig[:, ci], name="originale", line=dict(color="#22c55e", width=2)), 1, 1)
fig.add_trace(go.Scatter(y=recon[:, ci], name="copia dell'occhio", line=dict(color="#818cf8", width=2, dash="dash")), 1, 1)
fig.add_trace(go.Scatter(y=orig[:, ri], name="originale", line=dict(color="#22c55e", width=2), showlegend=False), 2, 1)
fig.add_trace(go.Scatter(y=recon[:, ri], name="copia", line=dict(color="#818cf8", width=2, dash="dash"), showlegend=False), 2, 1)

fig.update_layout(
    template="plotly_dark", height=720,
    title=dict(text="Verde = originale · Viola tratteggiato = copia dell'occhio. "
                    "Più si sovrappongono, meglio l'occhio ci vede.", x=0.5),
)
fig.write_html(str(OUT), include_plotlyjs=True)
print("✓ Immagine creata:", OUT.name)
