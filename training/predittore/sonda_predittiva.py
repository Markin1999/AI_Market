"""
Sonda predittiva — il test "da un milione di dollari": le forme prevedono?

Usa il modello GIÀ addestrato (nessuna nuova rete). In modo rigoroso:
  1. Sul PASSATO (train): per ogni forma calcola la direzione media futura
     ("dopo la forma #47, in media il prezzo sale o scende?").
  2. Sul FUTURO (test 2026, mai visto): vede una forma → predice su/giù
     secondo la tabella del passato → controlla se ci azzecca.
  3. Confronta con il BASELINE onesto (sempre la direzione più comune): la
     forma deve BATTERE quel baseline, altrimenti non aggiunge informazione.

Orizzonti: candele da 15 min → 4 = 1h, 16 = 4h, 64 = ~1 giorno.
Scrive a schermo e in logs/probe.log.

    python training/predittore/sonda_predittiva.py
    python training/predittore/sonda_predittiva.py --tickers 20   # più veloce
"""
import os
import sys
import logging
import argparse
from pathlib import Path

os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import numpy as np
import duckdb
import torch

from training import config
from training.data.windows import load_clean_series, _split_of, _SOURCE_COLS
from training.data.normalize import Normalizer
from training.occhio.architecture.vqvae import VQVAE

LOG_PATH = config.ROOT / "logs" / "probe.log"
LOG_PATH.parent.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(), logging.FileHandler(LOG_PATH)],
)
log = logging.getLogger("probe")

MODEL = config.MODELS_DIR / "occhio_vqvae.pt"
HORIZONS = [4, 16, 64]      # candele da 15 min → 1h, 4h, ~1 giorno
EVAL_STRIDE = 8             # campiona ogni 8 candele (riduce la sovrapposizione)
MIN_SAMPLES = 50           # forme con almeno N esempi nel passato per fidarsi


def get_device():
    return "mps" if torch.backends.mps.is_available() else "cpu"


def collect(model, device, limit_tickers):
    """Per ogni finestra: forma, split (train/test), rendimento futuro a ogni orizzonte."""
    norm = Normalizer(_SOURCE_COLS)
    W, maxH = config.WINDOW, max(HORIZONS)
    conn = duckdb.connect(str(config.DB_PATH), read_only=True)
    tickers = [r[0] for r in conn.execute("SELECT DISTINCT ticker FROM candles ORDER BY ticker").fetchall()]
    if limit_tickers:
        tickers = tickers[:limit_tickers]

    forms, splits = [], []
    rets = {h: [] for h in HORIZONS}
    for t in tickers:
        df = load_clean_series(conn, t)
        n = len(df)
        if n < W + maxH:
            continue
        arr = df[_SOURCE_COLS].to_numpy(np.float32)
        close = df["close"].to_numpy(np.float64)
        ts = df["ts"]
        starts = np.arange(0, n - W + 1 - maxH, EVAL_STRIDE)
        wins = np.stack([norm(arr[int(s):int(s) + W]) for s in starts])
        X = torch.from_numpy(wins).to(device)
        idxs = []
        with torch.no_grad():
            for i in range(0, len(X), 1024):
                z = model.encoder(X[i:i + 1024].transpose(1, 2))
                _, _, idx = model.quantizer(z)
                idxs.append(idx.cpu().numpy())
        idxs = np.concatenate(idxs)
        for j, s in enumerate(starts):
            e = int(s) + W - 1
            forms.append(int(idxs[j]))
            splits.append(_split_of(ts.iloc[e]))
            for h in HORIZONS:
                rets[h].append(close[e + h] / close[e] - 1.0)
    conn.close()
    return (np.array(forms), np.array(splits), {h: np.array(v) for h, v in rets.items()})


def run(forms, splits, rets):
    tr, te = splits == "train", splits == "test"
    log.info(f"campione: {len(forms):,} finestre · {tr.sum():,} passato · {te.sum():,} futuro (test)")
    results = {}
    for h in HORIZONS:
        r = rets[h]
        default = np.sign(r[tr].mean()) or 1.0            # direzione di fondo del mercato
        # tabella appresa sul PASSATO: direzione media per forma
        table = {}
        for f in np.unique(forms[tr]):
            m = tr & (forms == f)
            if m.sum() >= MIN_SAMPLES:
                table[f] = np.sign(r[m].mean()) or default
        # predizione sul FUTURO mai visto
        actual = np.sign(r[te])
        keep = actual != 0
        preds = np.array([table.get(f, default) for f in forms[te]])[keep]
        acts = actual[keep]
        acc = (preds == acts).mean() * 100
        up = (acts == 1).mean()
        majority = max(up, 1 - up) * 100                   # baseline onesto
        edge = acc - majority
        cov = np.mean([f in table for f in forms[te]]) * 100
        results[h] = (acc, majority, edge)
        label = {4: "1 ora", 16: "4 ore", 64: "~1 giorno"}[h]
        log.info(f"── Orizzonte {h} candele ({label}) ──")
        log.info(f"  precisione con le forme: {acc:.1f}%")
        log.info(f"  baseline (sempre la direzione comune): {majority:.1f}%")
        log.info(f"  VANTAGGIO della forma: {edge:+.1f} punti   (copertura forme: {cov:.0f}%)")
        verdict = ("✅ segnale" if edge >= 2 else "⚠️ debole" if edge >= 0.5 else "❌ nessun vantaggio")
        log.info(f"  → {verdict}")

    best = max(results.values(), key=lambda x: x[2])[2]
    log.info("=== RIEPILOGO ===")
    for h in HORIZONS:
        acc, maj, edge = results[h]
        log.info(f"  {h:>2} candele: {acc:.1f}% vs baseline {maj:.1f}%  → vantaggio {edge:+.1f}")
    log.info(f"  miglior vantaggio: {best:+.1f} punti")
    log.info("  " + (
        "✅ C'È SEGNALE: vale costruire lo Stadio 2 completo." if best >= 2 else
        "⚠️ SEGNALE DEBOLE: forse le forme attuali sono troppo grezze — da rinforzare." if best >= 0.5 else
        "❌ NESSUN VANTAGGIO: le forme da sole non prevedono. Ripensare l'approccio prima di investire."))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tickers", type=int, default=None)
    args = ap.parse_args()
    device = get_device()
    log.info(f"=== SONDA PREDITTIVA — le forme prevedono? — device: {device} ===")
    model = VQVAE().to(device)
    model.load_state_dict(torch.load(MODEL, map_location=device))
    model.eval()
    forms, splits, rets = collect(model, device, args.tickers)
    run(forms, splits, rets)


if __name__ == "__main__":
    main()
