"""
Passo 5 — I 3 test: l'occhio "ci vede" davvero?

  Test 1 — Ricostruzione su dati MAI VISTI (out-of-sample). Ridisegna bene il
           futuro quasi come il passato? → ha imparato strutture generali, non
           a memoria.
  Test 2 — Coerenza tra titoli (IL test chiave). La stessa forma compare su
           titoli diversi? → vede la forma, non il nome del titolo.
  Test 3 — Stabilità nel tempo. La stessa forma compare in anni diversi?
           → le forme di fondo restano, anche se il mercato cambia.

Scrive tutto a schermo E in logs/evaluation.log. Salva una mappa 2D delle firme
in models/pattern_memory/mappa_2d.html.

    python training/occhio/evaluate.py                 # tutti i 66 titoli
    python training/occhio/evaluate.py --tickers 20    # più veloce
"""
import os
import sys
import logging
import argparse
from pathlib import Path
from collections import defaultdict

os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import numpy as np
import duckdb
import torch
from torch.utils.data import DataLoader
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.manifold import TSNE

from training import config
from training.data.windows import CandleWindows, load_clean_series, _SOURCE_COLS
from training.data.normalize import Normalizer
from training.occhio.architecture.vqvae import VQVAE

LOG_PATH = config.ROOT / "logs" / "evaluation.log"
LOG_PATH.parent.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(), logging.FileHandler(LOG_PATH)],
)
log = logging.getLogger("evaluate")

MODEL = config.MODELS_DIR / "occhio_vqvae.pt"
MAP_OUT = config.PATTERN_MEMORY_DIR / "mappa_2d.html"


def get_device():
    return "mps" if torch.backends.mps.is_available() else "cpu"


def load_model(device):
    m = VQVAE().to(device)
    m.load_state_dict(torch.load(MODEL, map_location=device))
    m.eval()
    return m


# ── TEST 1 — ricostruzione su dati mai visti ─────────────────────────────────
def recon_error(model, ds, device, max_batches):
    loader = DataLoader(ds, batch_size=512, shuffle=True)
    loss_fn = torch.nn.MSELoss(reduction="sum")
    tot, n = 0.0, 0
    with torch.no_grad():
        for i, x in enumerate(loader):
            if i >= max_batches:
                break
            x = x.to(device)
            recon, _, _ = model(x)
            tot += loss_fn(recon, x).item()
            n += x.numel()
    return tot / n


def test1(model, device, args):
    log.info("── TEST 1 — Ricostruzione su dati mai visti ──")
    e_train = recon_error(model, CandleWindows("train", limit_tickers=args.tickers), device, args.max_batches)
    e_test = recon_error(model, CandleWindows("test", limit_tickers=args.tickers), device, args.max_batches)
    ratio = e_test / e_train if e_train > 0 else float("inf")
    log.info(f"  errore TRAIN (già visto): {e_train:.4f}")
    log.info(f"  errore TEST  (mai visto): {e_test:.4f}")
    log.info(f"  rapporto test/train: {ratio:.2f}×")
    ok = ratio <= 1.30
    log.info("  → " + ("✅ PASSA: ridisegna il futuro quasi come il passato → strutture generali"
                       if ok else "⚠️ ATTENZIONE: sul futuro molto peggio → rischio memorizzazione"))
    return ok


# ── Campione con metadati (titolo, anno) per i Test 2 e 3 ────────────────────
def sample_with_meta(model, device, per_ticker, limit_tickers):
    norm = Normalizer(_SOURCE_COLS)
    W = config.WINDOW
    rng = np.random.default_rng(0)
    conn = duckdb.connect(str(config.DB_PATH), read_only=True)
    tickers = [r[0] for r in conn.execute("SELECT DISTINCT ticker FROM candles ORDER BY ticker").fetchall()]
    if limit_tickers:
        tickers = tickers[:limit_tickers]

    Xs, tk, yr = [], [], []
    for t in tickers:
        df = load_clean_series(conn, t)
        if len(df) < W:
            continue
        arr = df[_SOURCE_COLS].to_numpy(np.float32)
        ts = df["ts"]
        starts = np.arange(0, len(df) - W + 1, config.STRIDE)
        if len(starts) > per_ticker:
            starts = rng.choice(starts, per_ticker, replace=False)
        for s in starts:
            Xs.append(norm(arr[int(s):int(s) + W]))
            tk.append(t)
            yr.append(str(ts.iloc[int(s) + W - 1])[:4])
    conn.close()

    X = torch.from_numpy(np.stack(Xs)).to(device)
    sigs, forms = [], []
    with torch.no_grad():
        for i in range(0, len(X), 512):
            z = model.encoder(X[i:i + 512].transpose(1, 2))
            _, _, idx = model.quantizer(z)
            sigs.append(z.cpu().numpy())
            forms.append(idx.cpu().numpy())
    return np.concatenate(sigs), np.concatenate(forms), np.array(tk), np.array(yr)


# ── TEST 2 — coerenza tra titoli ─────────────────────────────────────────────
def test2(forms, tickers):
    log.info("── TEST 2 — Coerenza tra titoli (il test chiave) ──")
    by_form = defaultdict(set)
    for f, t in zip(forms, tickers):
        by_form[f].add(t)
    counts = np.array([len(s) for s in by_form.values()])
    avg = counts.mean()
    multi = (counts >= 5).mean() * 100
    log.info(f"  forme attive: {len(counts)} · titoli nel campione: {len(set(tickers))}")
    log.info(f"  titoli diversi per forma (media): {avg:.1f}")
    log.info(f"  forme condivise da ≥5 titoli: {multi:.0f}%")
    ok = avg >= 3 and multi >= 50
    log.info("  → " + ("✅ PASSA: le forme compaiono su molti titoli → vede la forma, non il nome"
                       if ok else "⚠️ ATTENZIONE: forme legate a pochi titoli → potrebbe legarsi al titolo"))
    return ok


# ── TEST 3 — stabilità nel tempo ─────────────────────────────────────────────
def test3(forms, years):
    log.info("── TEST 3 — Stabilità nel tempo ──")
    by_form = defaultdict(set)
    for f, y in zip(forms, years):
        by_form[f].add(y)
    counts = np.array([len(s) for s in by_form.values()])
    avg = counts.mean()
    multi = (counts >= 3).mean() * 100
    log.info(f"  anni nel campione: {len(set(years))}")
    log.info(f"  anni diversi per forma (media): {avg:.1f}")
    log.info(f"  forme presenti in ≥3 anni: {multi:.0f}%")
    ok = avg >= 2 and multi >= 50
    log.info("  → " + ("✅ PASSA: le forme tornano in anni diversi → strutture di fondo stabili"
                       if ok else "⚠️ ATTENZIONE: forme legate a un solo anno → poco stabili"))
    return ok


# ── Mappa 2D (t-SNE) ─────────────────────────────────────────────────────────
def draw_map(sigs, tickers, years):
    n = min(3000, len(sigs))
    idx = np.random.default_rng(0).choice(len(sigs), n, replace=False)
    log.info(f"Disegno la mappa 2D (t-SNE su {n} punti)... ~1 min")
    emb = TSNE(n_components=2, init="pca", perplexity=30, random_state=0).fit_transform(sigs[idx])
    tks, yrs = tickers[idx], years[idx]
    fig = make_subplots(rows=1, cols=2, subplot_titles=["Colorato per TITOLO", "Colorato per ANNO"])
    for t in sorted(set(tks)):
        m = tks == t
        fig.add_trace(go.Scatter(x=emb[m, 0], y=emb[m, 1], mode="markers", name=str(t),
                                 marker=dict(size=3), showlegend=False), 1, 1)
    for y in sorted(set(yrs)):
        m = yrs == y
        fig.add_trace(go.Scatter(x=emb[m, 0], y=emb[m, 1], mode="markers", name=str(y),
                                 marker=dict(size=3)), 1, 2)
    fig.update_layout(
        template="plotly_dark", height=620,
        title=dict(x=0.5, text="Mappa 2D delle firme — se DENTRO ogni gruppo i colori sono "
                               "MESCOLATI, l'occhio vede la forma (non il titolo né l'anno)"),
    )
    fig.write_html(str(MAP_OUT), include_plotlyjs=True)
    log.info(f"  ✓ mappa salvata: {MAP_OUT.relative_to(config.ROOT)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tickers", type=int, default=None, help="limita a N titoli")
    ap.add_argument("--max-batches", type=int, default=80, help="blocchi per il Test 1")
    ap.add_argument("--per-ticker", type=int, default=300, help="finestre per titolo (Test 2/3)")
    args = ap.parse_args()

    device = get_device()
    log.info(f"=== VALUTAZIONE — i 3 test — device: {device} ===")
    model = load_model(device)

    r1 = test1(model, device, args)

    log.info("Campiono finestre con metadati (titolo, anno)...")
    sigs, forms, tickers, years = sample_with_meta(model, device, args.per_ticker, args.tickers)
    log.info(f"  campione: {len(sigs):,} finestre · {len(set(tickers))} titoli · {len(set(years))} anni")
    r2 = test2(forms, tickers)
    r3 = test3(forms, years)
    draw_map(sigs, tickers, years)

    log.info("=== RIEPILOGO ===")
    log.info(f"  Test 1 (out-of-sample): {'✅ PASSA' if r1 else '⚠️ ATTENZIONE'}")
    log.info(f"  Test 2 (tra titoli):    {'✅ PASSA' if r2 else '⚠️ ATTENZIONE'}")
    log.info(f"  Test 3 (nel tempo):     {'✅ PASSA' if r3 else '⚠️ ATTENZIONE'}")
    log.info(f"  → {sum([r1, r2, r3])}/3 test superati")


if __name__ == "__main__":
    main()
