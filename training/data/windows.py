"""
Passo 2 — Tagliare la storia in finestre da un giorno + split train/val/test.

Le finestre NON si salvano su disco (sarebbero decine di GB): si generano AL VOLO
da una serie per-titolo tenuta in memoria come array numpy float32 (~700 MB sul
totale). Dato un indice, il Dataset estrae una finestra e la normalizza (veloce).

Split per DATA (il test è un periodo FUTURO): una finestra appartiene a un insieme
in base alla data della sua ULTIMA candela.

Verifica rapida:
    python training/data/windows.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import numpy as np
import duckdb
import torch
from torch.utils.data import Dataset

from training import config
from training.data.normalize import Normalizer

# Colonne sorgente da leggere dal DB (oltre a ts), senza duplicati
_SOURCE_COLS = list(dict.fromkeys(
    config.PRICE_GROUP + ["volume"] + config.UNBOUNDED
    + config.BOUNDED_0_100 + config.BOUNDED_PM_100 + config.BOUNDED_NEG_100
    + config.PATTERNS
))


def load_clean_series(conn, ticker):
    """Candele di un titolo, ordinate, senza le righe di warmup (NaN negli indicatori)."""
    cols = ", ".join(["ts"] + _SOURCE_COLS)
    df = conn.execute(
        f"SELECT {cols} FROM candles WHERE ticker = ? ORDER BY ts", [ticker]
    ).df()
    return df.dropna(subset=_SOURCE_COLS).reset_index(drop=True)


def _split_of(end_date) -> str:
    d = str(end_date)[:10]
    if d <= config.TRAIN_END:
        return "train"
    if d <= config.VAL_END:
        return "val"
    return "test"


class CandleWindows(Dataset):
    """Finestre da config.WINDOW candele, normalizzate, per un dato split."""

    def __init__(self, split, tickers=None, limit_tickers=None):
        assert split in ("train", "val", "test")
        self.split = split
        self.norm = Normalizer(_SOURCE_COLS)
        W = config.WINDOW

        conn = duckdb.connect(str(config.DB_PATH), read_only=True)
        if tickers is None:
            tickers = [r[0] for r in conn.execute(
                "SELECT DISTINCT ticker FROM candles ORDER BY ticker"
            ).fetchall()]
        if limit_tickers:
            tickers = tickers[:limit_tickers]

        self.series = {}     # ticker -> array numpy float32 (righe x colonne sorgente)
        self.index = []      # lista di (ticker, start)
        for t in tickers:
            df = load_clean_series(conn, t)
            if len(df) < W:
                continue
            self.series[t] = df[_SOURCE_COLS].to_numpy(np.float32)
            ts = df["ts"]
            for start in range(0, len(df) - W + 1, config.STRIDE):
                if _split_of(ts.iloc[start + W - 1]) == split:
                    self.index.append((t, start))
        conn.close()

    def __len__(self):
        return len(self.index)

    def __getitem__(self, i):
        t, start = self.index[i]
        arr = self.series[t][start:start + config.WINDOW]
        return torch.from_numpy(self.norm(arr))


def _report(limit_tickers=3):
    print(f"Costruzione finestre su {limit_tickers} titoli (campione di verifica)...\n")
    for split in ("train", "val", "test"):
        ds = CandleWindows(split, limit_tickers=limit_tickers)
        n = len(ds)
        if n == 0:
            print(f"  {split:5}: 0 finestre")
            continue
        x = ds[0]
        print(f"  {split:5}: {n:>9,} finestre | forma {tuple(x.shape)} "
              f"| valori [{x.min():+.2f}, {x.max():+.2f}] | NaN: {bool(torch.isnan(x).any())}")
    print(f"\n  Feature per candela : {len(config.FEATURE_COLS)}")
    print(f"  Finestra            : {config.WINDOW} candele (= 1 giorno)")
    print(f"  Split (per data)    : train ≤ {config.TRAIN_END} < val ≤ {config.VAL_END} < test")


if __name__ == "__main__":
    _report()
