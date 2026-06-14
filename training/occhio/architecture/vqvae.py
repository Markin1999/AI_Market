"""
L'occhio assemblato.

Passo A: Autoencoder = encoder + decoder. Impara a RICOPIARE le finestre.
Passo B: VQ-VAE = encoder + DIZIONARIO + decoder. Oltre a ricopiare, aggancia
         ogni giorno alla forma più simile del dizionario → da qui nasce la
         libreria dei pattern.
"""
import torch.nn as nn

from training import config
from training.occhio.architecture.encoder import Encoder
from training.occhio.architecture.decoder import Decoder
from training.occhio.architecture.quantizer import VectorQuantizer


class Autoencoder(nn.Module):
    """L'occhio che ricopia (encoder + decoder, senza dizionario)."""

    def __init__(self, n_features: int = None, signature_dim: int = None):
        super().__init__()
        n_features = n_features or len(config.FEATURE_COLS)
        signature_dim = signature_dim or config.SIGNATURE_DIM
        self.encoder = Encoder(n_features, signature_dim)
        self.decoder = Decoder(n_features, signature_dim)

    def forward(self, x):                 # x: (B, WINDOW, n_features)
        z = self.encoder(x.transpose(1, 2))
        recon = self.decoder(z)
        return recon.transpose(1, 2)

    def encode(self, x):
        return self.encoder(x.transpose(1, 2))


class VQVAE(nn.Module):
    """L'occhio col dizionario: encoder → dizionario → decoder."""

    def __init__(self, n_features: int = None, signature_dim: int = None, codebook_size: int = None):
        super().__init__()
        n_features = n_features or len(config.FEATURE_COLS)
        signature_dim = signature_dim or config.SIGNATURE_DIM
        codebook_size = codebook_size or config.CODEBOOK_SIZE
        self.encoder = Encoder(n_features, signature_dim)
        self.quantizer = VectorQuantizer(codebook_size, signature_dim)
        self.decoder = Decoder(n_features, signature_dim)

    def forward(self, x):                 # x: (B, WINDOW, n_features)
        z = self.encoder(x.transpose(1, 2))   # firma
        zq, vq_loss, idx = self.quantizer(z)  # forma del dizionario
        recon = self.decoder(zq).transpose(1, 2)
        return recon, vq_loss, idx

    def code_of(self, x):
        """Quale forma del dizionario (numero) per ogni finestra."""
        z = self.encoder(x.transpose(1, 2))
        _, _, idx = self.quantizer(z)
        return idx

    def shape_of_code(self, code_idx):
        """Disegna la forma corrispondente a una voce del dizionario."""
        zq = self.quantizer.codebook(code_idx)
        return self.decoder(zq).transpose(1, 2)
