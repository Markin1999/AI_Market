"""
Passo 4 — Tira fuori la LIBRERIA: disegna le forme del dizionario.

Conta quali forme del dizionario l'occhio usa di più, prende le più frequenti,
le fa ridisegnare e le salva come grafici in models/pattern_memory/. È il tuo
"database di grafici" da aprire e sfogliare.

    python training/occhio/pattern_memory.py --tickers 10
"""
import os
import sys
import argparse
from pathlib import Path

os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import numpy as np
import torch
from torch.utils.data import DataLoader
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from training import config
from training.data.windows import CandleWindows
from training.occhio.architecture.vqvae import VQVAE

MODEL = config.MODELS_DIR / "occhio_vqvae.pt"
OUTDIR = config.PATTERN_MEMORY_DIR
OUT_HTML = OUTDIR / "libreria.html"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tickers", type=int, default=10)
    ap.add_argument("--top", type=int, default=24, help="quante forme mostrare")
    args = ap.parse_args()

    OUTDIR.mkdir(parents=True, exist_ok=True)
    model = VQVAE()
    model.load_state_dict(torch.load(MODEL, map_location="cpu"))
    model.eval()

    # Conta quanto viene usata ogni forma del dizionario
    print("Conto l'uso delle forme...")
    ds = CandleWindows("train", limit_tickers=args.tickers)
    loader = DataLoader(ds, batch_size=512)
    counts = torch.zeros(config.CODEBOOK_SIZE, dtype=torch.long)
    with torch.no_grad():
        for x in loader:
            idx = model.code_of(x)
            counts += torch.bincount(idx, minlength=config.CODEBOOK_SIZE)
    used = int((counts > 0).sum())
    top = counts.argsort(descending=True)[:args.top]

    # Salva i vettori del dizionario (per memoria)
    np.save(OUTDIR / "codebook.npy", model.quantizer.codebook.weight.detach().numpy())

    # Disegna la forma (linea del prezzo) di ogni voce più usata
    ci = config.FEATURE_COLS.index("close")
    cols = 6
    rows = (args.top + cols - 1) // cols
    fig = make_subplots(rows=rows, cols=cols,
                        subplot_titles=[f"forma #{int(c)} — {int(counts[c]):,} volte" for c in top])
    with torch.no_grad():
        for j, c in enumerate(top):
            shape = model.shape_of_code(torch.tensor([int(c)]))[0].numpy()  # (WINDOW, n_feature)
            r, cc = j // cols + 1, j % cols + 1
            fig.add_trace(go.Scatter(y=shape[:, ci], line=dict(color="#818cf8", width=2)), row=r, col=cc)

    fig.update_layout(
        template="plotly_dark", height=190 * rows, showlegend=False,
        title=dict(text=f"Libreria dei pattern — {used}/{config.CODEBOOK_SIZE} forme usate · "
                        f"le {args.top} più frequenti (forma del prezzo)", x=0.5),
    )
    fig.update_xaxes(showticklabels=False)
    fig.write_html(str(OUT_HTML), include_plotlyjs=True)
    print(f"✓ Libreria salvata in {OUT_HTML.relative_to(config.ROOT)}")
    print(f"  Forme del dizionario usate: {used}/{config.CODEBOOK_SIZE}")


if __name__ == "__main__":
    main()
