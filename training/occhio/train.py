"""
Passo 3-4 — Addestramento dell'occhio.

  --model auto   : Passo 3, autoencoder (impara a ricopiare)
  --model vqvae  : Passo 4, col dizionario (impara a ricopiare E a usare le forme)

Mostra una finestra all'occhio, lui la ridisegna, si misura l'errore e si corregge.
Tutto viene scritto IN TEMPO REALE in logs/training.log (oltre che a schermo):
    tail -f logs/training.log

    python training/occhio/train.py --model vqvae --tickers 10 --epochs 6   # test
    python training/occhio/train.py --model vqvae                           # tutto
"""
import os
import sys
import time
import logging
import argparse
from pathlib import Path

os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import torch
from torch.utils.data import DataLoader

from training import config
from training.data.windows import CandleWindows
from training.occhio.architecture.vqvae import Autoencoder, VQVAE

LOG_PATH = config.ROOT / "logs" / "training.log"
LOG_PATH.parent.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(), logging.FileHandler(LOG_PATH)],
)
log = logging.getLogger("training")


def get_device():
    return "mps" if torch.backends.mps.is_available() else "cpu"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tickers", type=int, default=None, help="limita a N titoli (per il test)")
    ap.add_argument("--epochs", type=int, default=config.EPOCHS)
    ap.add_argument("--model", choices=["auto", "vqvae"], default="vqvae")
    args = ap.parse_args()

    is_vq = args.model == "vqvae"
    device = get_device()
    scope = f"{args.tickers} titoli" if args.tickers else "TUTTI i titoli"
    nome = "VQ-VAE (col dizionario)" if is_vq else "Autoencoder (ricopia)"
    log.info(f"=== Addestramento {nome} — {scope} — device: {device} ===")

    log.info("Carico le finestre di training dal database...")
    train_ds = CandleWindows("train", limit_tickers=args.tickers)
    log.info(f"  {len(train_ds):,} finestre da {config.WINDOW} candele × {len(config.FEATURE_COLS)} feature")
    loader = DataLoader(train_ds, batch_size=config.BATCH_SIZE, shuffle=True, drop_last=True)

    model = (VQVAE() if is_vq else Autoencoder()).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=config.LEARNING_RATE)
    loss_fn = torch.nn.MSELoss()
    n_params = sum(p.numel() for p in model.parameters())
    extra = f" | dizionario da {config.CODEBOOK_SIZE} forme" if is_vq else ""
    log.info(f"Occhio: {n_params:,} parametri | firma da {config.SIGNATURE_DIM} numeri{extra} | {len(loader)} blocchi/epoca")

    for epoch in range(1, args.epochs + 1):
        model.train()
        tot_recon, n, t0 = 0.0, 0, time.time()
        used = torch.zeros(config.CODEBOOK_SIZE, device=device) if is_vq else None
        for x in loader:
            x = x.to(device)
            if is_vq:
                recon, vq_loss, idx = model(x)
                recon_loss = loss_fn(recon, x)
                loss = recon_loss + vq_loss
                used[idx] = 1
            else:
                recon = model(x)
                recon_loss = loss = loss_fn(recon, x)
            opt.zero_grad()
            loss.backward()
            opt.step()
            tot_recon += recon_loss.item() * x.size(0)
            n += x.size(0)

        msg = f"  Epoca {epoch:>2}/{args.epochs}: errore di ricopiatura = {tot_recon / n:.4f}"
        if is_vq:
            msg += f" | dizionario usato {int(used.sum())}/{config.CODEBOOK_SIZE} forme"
        msg += f"  ({time.time() - t0:.0f}s)"
        log.info(msg)

    config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    out = config.MODELS_DIR / ("occhio_vqvae.pt" if is_vq else "occhio_autoencoder.pt")
    torch.save(model.state_dict(), out)
    log.info(f"✓ Occhio salvato in {out.relative_to(config.ROOT)}")
    if is_vq:
        log.info("  Ora tira fuori la libreria:  python training/occhio/pattern_memory.py --tickers 10")
    log.info("=== Fine addestramento ===")


if __name__ == "__main__":
    main()
