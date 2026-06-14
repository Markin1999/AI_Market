"""
Il decoder: ricostruisce (ridisegna) la finestra partendo dalla firma.

Specchio dell'encoder: dalla firma torna su, con due strati convoluzionali
"al contrario", fino a riottenere una finestra della forma originale.
"""
import torch.nn as nn

from training import config


class Decoder(nn.Module):
    def __init__(self, n_features: int, signature_dim: int):
        super().__init__()
        self.lin = nn.Linear(signature_dim, 128 * (config.WINDOW // 4))
        self.net = nn.Sequential(
            nn.ReLU(),
            nn.ConvTranspose1d(128, 64, kernel_size=4, stride=2, padding=1),         # 16 -> 32
            nn.ReLU(),
            nn.ConvTranspose1d(64, n_features, kernel_size=4, stride=2, padding=1),  # 32 -> 64
        )

    def forward(self, z):          # z: (B, signature_dim)
        x = self.lin(z).view(z.size(0), 128, config.WINDOW // 4)
        return self.net(x)         # (B, n_features, WINDOW)
