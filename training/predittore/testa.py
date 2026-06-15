"""
La TESTA del predittore (IA #2) — Fase 3.

Una piccola rete che si appoggia SOPRA l'occhio (congelato). Riceve la lettura
dell'occhio (la firma) + gli indicatori della candela attuale, e stima il
movimento della PROSSIMA candela: un numero in %, dove
  • il SEGNO è la direzione   (+ sale / − scende)
  • il VALORE ASSOLUTO è "di quanto".
"""
import torch.nn as nn


class Testa(nn.Module):
    def __init__(self, n_in: int, hidden: int = 64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_in, hidden), nn.ReLU(),
            nn.Linear(hidden, hidden), nn.ReLU(),
            nn.Linear(hidden, 1),
        )

    def forward(self, x):                  # x: (B, n_in) = firma + indicatori
        return self.net(x).squeeze(-1)     # (B,) stima del rendimento % alla prossima candela
