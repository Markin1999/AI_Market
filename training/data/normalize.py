"""
Passo 2 — Normalizzazione di una finestra: forma + indicatori alla stessa scala.

Ogni finestra viene normalizzata DA SOLA, così una salita del 2% di NVDA e una
di KO diventano identiche: conta la forma, non il titolo né il prezzo assoluto.
Senza, i numeri grandi (OBV nei milioni) schiacciano i piccoli (RSI 0-100).

Regole per famiglia (definite in config):
  • gruppo prezzo (OHLC, VWAP, EMA, Bollinger, Donchian, Keltner, Ichimoku):
        normalizzati INSIEME con media/dev.std del CLOSE → relazioni preservate
  • volume: media/dev.std della finestra
  • indicatori senza scala fissa (MACD, ATR, ROC, CCI, OBV, CMF, Force Index):
        z-score nella finestra, colonna per colonna
  • indicatori 0-100 (RSI, Stoch, MFI, ADX, Aroon up/down): x/50 - 1  → -1..+1
  • Aroon oscillatore (-100..+100): x/100
  • Williams %R (-100..0): (x+50)/50  → -1..+1
  • pattern candele (100/0/-100): x/100  → +1/0/-1

Lavora su array numpy (veloce): riceve una finestra (WINDOW, n_colonne_sorgente)
e restituisce (WINDOW, n_feature) nell'ordine FEATURE_COLS.
"""
import numpy as np

from training import config

_EPS = 1e-8


class Normalizer:
    def __init__(self, source_cols):
        idx = {c: i for i, c in enumerate(source_cols)}
        self.close = idx["close"]
        self.vol   = idx["volume"]
        self.price = [idx[c] for c in config.PRICE_GROUP]
        self.unb   = [idx[c] for c in config.UNBOUNDED]
        self.b100  = [idx[c] for c in config.BOUNDED_0_100]
        self.bpm   = [idx[c] for c in config.BOUNDED_PM_100]
        self.bneg  = [idx[c] for c in config.BOUNDED_NEG_100]
        self.pat   = [idx[c] for c in config.PATTERNS]

    def __call__(self, arr: np.ndarray) -> np.ndarray:
        # Gruppo prezzo: riferimento comune = media/dev.std del close
        c = arr[:, self.close]
        m, s = c.mean(), c.std() + _EPS
        price = (arr[:, self.price] - m) / s

        # Volume: z-score
        v = arr[:, self.vol]
        vol = ((v - v.mean()) / (v.std() + _EPS))[:, None]

        # Indicatori senza scala: z-score colonna per colonna
        u = arr[:, self.unb]
        unb = (u - u.mean(axis=0)) / (u.std(axis=0) + _EPS)

        # Indicatori a scala fissa → -1..+1
        b100 = arr[:, self.b100] / 50.0 - 1.0
        bpm  = arr[:, self.bpm] / 100.0
        bneg = (arr[:, self.bneg] + 50.0) / 50.0
        pat  = arr[:, self.pat] / 100.0

        out = np.concatenate([price, vol, unb, b100, bpm, bneg, pat], axis=1)
        return out.astype(np.float32)
