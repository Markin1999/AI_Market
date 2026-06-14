"""
L'occhio — encoder: comprime una finestra (un giorno) in una "firma".

Usa due strati convoluzionali 1D (scorrono lungo il tempo, ideali per le forme
dei grafici) e poi schiaccia tutto in un vettore di config.SIGNATURE_DIM numeri.
"""
import torch.nn as nn

from training import config


class Encoder(nn.Module):
    def __init__(self, n_features: int, signature_dim: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv1d(n_features, 64, kernel_size=4, stride=2, padding=1),  # 64 -> 32
            nn.ReLU(),
            nn.Conv1d(64, 128, kernel_size=4, stride=2, padding=1),         # 32 -> 16
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(128 * (config.WINDOW // 4), signature_dim),
        )

    def forward(self, x):          # x: (B, n_features, WINDOW)
        return self.net(x)         # (B, signature_dim)
