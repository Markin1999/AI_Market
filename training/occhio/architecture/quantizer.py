"""
Il dizionario di forme (codebook) — il cuore del Passo 4.

Riceve la "firma" di un giorno e la AGGANCIA alla forma più simile tra le K del
dizionario. È come arrotondare una parola alla più vicina di un vocabolario
limitato. Durante l'addestramento, le forme del dizionario si spostano per
descrivere sempre meglio i grafici reali.
"""
import torch
import torch.nn as nn


class VectorQuantizer(nn.Module):
    def __init__(self, n_codes: int, dim: int, beta: float = 0.25):
        super().__init__()
        self.n_codes = n_codes
        self.beta = beta
        self.codebook = nn.Embedding(n_codes, dim)
        self.codebook.weight.data.uniform_(-1.0 / n_codes, 1.0 / n_codes)

    def forward(self, z):                      # z: (B, dim) — la firma
        # Distanza della firma da ogni forma del dizionario
        d = (z.pow(2).sum(1, keepdim=True)
             - 2 * z @ self.codebook.weight.t()
             + self.codebook.weight.pow(2).sum(1))
        idx = d.argmin(1)                      # la forma più vicina (per ogni firma)
        zq = self.codebook(idx)               # la forma scelta dal dizionario

        # Il "trucco" per allenare il dizionario: la firma deve avvicinarsi alla
        # forma scelta, e la forma alla firma.
        loss = (self.beta * (z - zq.detach()).pow(2).mean()
                + (zq - z.detach()).pow(2).mean())

        # Straight-through: in avanti usa zq, ma il gradiente passa a z
        zq = z + (zq - z).detach()
        return zq, loss, idx
