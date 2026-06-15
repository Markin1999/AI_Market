"""
Fase 3 — Costruire e allenare la TESTA che predice (IA #2).

Sopra l'occhio CONGELATO: per ogni finestra calcola la firma (32) + prende gli
indicatori della candela attuale (47) → la testa stima il movimento della
PROSSIMA candela (in %: segno = su/giù, valore = di quanto).

Stessa filosofia dell'occhio:
  • si allena sul PASSATO (≤ 2025-06-30)
  • si controlla in continuo sulla VALIDAZIONE (2025-07 → 2025-12)
  • giudizio finale sul FUTURO mai visto (test = 2026)
Confronto sempre col BASELINE (la direzione più comune). Soglia roadmap: >53%.
Log in logs/predittore.log.

    python training/predittore/train_predittore.py                 # tutti i titoli
    python training/predittore/train_predittore.py --tickers 20    # più veloce
    python training/predittore/train_predittore.py --horizon 16    # 4 ore avanti
"""
import os
import sys
import time
import logging
import argparse
from pathlib import Path

os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import numpy as np
import duckdb
import torch
from torch.utils.data import DataLoader, TensorDataset

from training import config
from training.data.windows import load_clean_series, _split_of, _SOURCE_COLS
from training.data.normalize import Normalizer
from training.occhio.architecture.vqvae import VQVAE
from training.predittore.testa import Testa

LOG_PATH = config.ROOT / "logs" / "predittore.log"
LOG_PATH.parent.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(), logging.FileHandler(LOG_PATH)],
)
log = logging.getLogger("predittore")

EYE = config.MODELS_DIR / "occhio_vqvae.pt"
OUT = config.MODELS_DIR / "predittore_testa.pt"

# Parametri (i numeri in un posto)
TRAIN_STRIDE = 4     # campiona ogni 4 candele (riduce le finestre fotocopia)
HIDDEN = 64
EPOCHS = 15
BATCH = 1024
LR = 1e-3


def get_device():
    return "mps" if torch.backends.mps.is_available() else "cpu"


def build_features(model, device, limit_tickers, horizon):
    """Per ogni finestra: [firma(32) + indicatori ultima candela(47)], rendimento % futuro, split."""
    norm = Normalizer(_SOURCE_COLS)
    W = config.WINDOW
    conn = duckdb.connect(str(config.DB_PATH), read_only=True)
    tickers = [r[0] for r in conn.execute("SELECT DISTINCT ticker FROM candles ORDER BY ticker").fetchall()]
    if limit_tickers:
        tickers = tickers[:limit_tickers]

    feats, rets, splits = [], [], []
    for t in tickers:
        df = load_clean_series(conn, t)
        n = len(df)
        if n < W + horizon:
            continue
        arr = df[_SOURCE_COLS].to_numpy(np.float32)
        close = df["close"].to_numpy(np.float64)
        ts = df["ts"]
        starts = np.arange(0, n - W + 1 - horizon, TRAIN_STRIDE)
        wins = np.stack([norm(arr[int(s):int(s) + W]) for s in starts])   # (k, W, 47)
        Xw = torch.from_numpy(wins).to(device)
        sig = []
        with torch.no_grad():
            for i in range(0, len(Xw), 1024):
                sig.append(model.encoder(Xw[i:i + 1024].transpose(1, 2)).cpu().numpy())
        sig = np.concatenate(sig)                  # (k, 32) la firma
        feat = np.concatenate([sig, wins[:, -1, :]], axis=1)  # + indicatori candela attuale → (k, 79)
        for j, s in enumerate(starts):
            e = int(s) + W - 1
            feats.append(feat[j])
            rets.append((close[e + horizon] / close[e] - 1.0) * 100.0)   # rendimento in %
            splits.append(_split_of(ts.iloc[e]))
    conn.close()
    return np.asarray(feats, np.float32), np.asarray(rets, np.float32), np.asarray(splits)


def direction_stats(pred, actual):
    """accuracy direzionale (%) e baseline (direzione più comune, %)."""
    keep = actual != 0
    p, a = np.sign(pred[keep]), np.sign(actual[keep])
    acc = (p == a).mean() * 100
    up = (a == 1).mean()
    baseline = max(up, 1 - up) * 100
    return acc, baseline


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tickers", type=int, default=None)
    ap.add_argument("--horizon", type=int, default=1, help="candele avanti (1 = candela successiva)")
    ap.add_argument("--epochs", type=int, default=EPOCHS)
    args = ap.parse_args()

    device = get_device()
    label = {1: "candela successiva (15 min)", 16: "4 ore", 64: "~1 giorno"}.get(args.horizon, f"{args.horizon} candele")
    log.info(f"=== Addestramento TESTA (predittore) — orizzonte: {label} — device: {device} ===")

    # 1. Occhio CONGELATO → firma per ogni finestra
    eye = VQVAE().to(device)
    eye.load_state_dict(torch.load(EYE, map_location=device))
    eye.eval()
    log.info("Calcolo firma + indicatori per tutte le finestre (occhio congelato)...")
    X, y, sp = build_features(eye, device, args.tickers, args.horizon)
    tr, va, te = sp == "train", sp == "val", sp == "test"
    log.info(f"  {len(X):,} finestre · {tr.sum():,} train · {va.sum():,} val · {te.sum():,} test · {X.shape[1]} ingressi")

    # 2. La testa che impara
    head = Testa(X.shape[1], HIDDEN).to(device)
    opt = torch.optim.Adam(head.parameters(), lr=LR)
    loss_fn = torch.nn.SmoothL1Loss()        # Huber: robusto agli scatti estremi
    Xtr = torch.from_numpy(X[tr]).to(device); ytr = torch.from_numpy(y[tr]).to(device)
    Xva = torch.from_numpy(X[va]).to(device); yva_np = y[va]
    loader = DataLoader(TensorDataset(Xtr, ytr), batch_size=BATCH, shuffle=True)
    n_params = sum(p.numel() for p in head.parameters())
    log.info(f"Testa: {n_params:,} parametri | {len(loader)} blocchi/epoca")

    for epoch in range(1, args.epochs + 1):
        head.train()
        tot, n, t0 = 0.0, 0, time.time()
        for xb, yb in loader:
            loss = loss_fn(head(xb), yb)
            opt.zero_grad(); loss.backward(); opt.step()
            tot += loss.item() * xb.size(0); n += xb.size(0)
        head.eval()
        with torch.no_grad():
            pred_va = head(Xva).cpu().numpy()
        acc, base = direction_stats(pred_va, yva_np)
        log.info(f"  Epoca {epoch:>2}/{args.epochs}: perdita {tot / n:.4f} | "
                 f"validazione: direzione {acc:.1f}% (baseline {base:.1f}%)  ({time.time() - t0:.0f}s)")

    # 3. Giudizio finale sul FUTURO mai visto (test = 2026)
    head.eval()
    with torch.no_grad():
        pred_te = head(torch.from_numpy(X[te]).to(device)).cpu().numpy()
    acc, base = direction_stats(pred_te, y[te])
    mae = np.abs(pred_te - y[te]).mean()
    log.info("=== GIUDIZIO FINALE (test 2026, mai visto) ===")
    log.info(f"  direzione (su/giù): {acc:.1f}%   vs baseline {base:.1f}%   → vantaggio {acc - base:+.1f}")
    log.info(f"  errore sulla grandezza (MAE): {mae:.3f}%")
    verdict = ("✅ C'È VANTAGGIO: la testa batte il baseline." if acc - base >= 1.0 else
               "⚠️ vantaggio minimo." if acc - base >= 0.3 else
               "❌ nessun vantaggio: la direzione non è prevedibile da questi ingressi.")
    log.info(f"  → {verdict}")

    config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    torch.save(head.state_dict(), OUT)
    log.info(f"✓ Testa salvata in {OUT.relative_to(config.ROOT)}")
    log.info("=== Fine ===")


if __name__ == "__main__":
    main()
