"""
Configurazione dello Stadio 1 (Vedere) — tutti i numeri in un posto.

Le scelte sono spiegate nel README di questa cartella. Sono punti di partenza:
si regoleranno guardando i primi risultati reali, come prescrive la filosofia.
"""
from pathlib import Path

# ── Percorsi (la root del progetto è due livelli sopra questo file) ──────────
ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "raw" / "market.duckdb"
MODELS_DIR = ROOT / "models"
PATTERN_MEMORY_DIR = MODELS_DIR / "pattern_memory"

# ── La finestra: il "colpo d'occhio" ─────────────────────────────────────────
WINDOW = 64          # candele per finestra = 1 giorno di mercato
STRIDE = 1           # di quanto scorre la finestra (1 = massima sovrapposizione)

# ── Divisione temporale (il TEST è un periodo FUTURO, mai scelto a caso) ─────
# Il DB copre 2021-06 → 2026-06. Date di partenza, da rivedere sui dati reali:
TRAIN_END = "2025-06-30"   # fino a qui: addestramento
VAL_END   = "2025-12-31"   # da TRAIN_END a qui: validazione; dopo: test

# ── L'occhio (il modello) ────────────────────────────────────────────────────
SIGNATURE_DIM = 32    # quanto comprime: dimensione della "firma" di una finestra
CODEBOOK_SIZE = 256   # quante forme nel dizionario (Passo B — VQ-VAE)

# ── Addestramento ────────────────────────────────────────────────────────────
BATCH_SIZE = 256
EPOCHS = 20
LEARNING_RATE = 1e-3
# Il device (GPU "mps" del Mac, oppure "cpu") viene scelto a runtime in train.py.

# ── Le feature di input (cosa vede l'occhio per ogni candela) ────────────────
# Raggruppate per COME si normalizzano (vedi data/normalize.py).
#
# Gruppo PREZZO: normalizzato insieme col riferimento del close della finestra,
# così le relazioni (prezzo vs media vs banda) restano coerenti.
PRICE_GROUP = [
    "open", "high", "low", "close", "vwap",
    "ema_20", "ema_50", "ema_200",
    "bb_upper", "bb_mid", "bb_lower",
    "dc_upper", "dc_lower", "kc_upper", "kc_lower",
    "ichi_tenkan", "ichi_kijun",
]
# Indicatori senza scala fissa: z-score nella finestra, colonna per colonna.
UNBOUNDED = [
    "macd", "macd_signal", "macd_hist",
    "atr", "roc", "cci", "obv", "cmf", "force_index",
]
# Indicatori a scala fissa: mappati linearmente in -1..+1 (mantengono il significato).
BOUNDED_0_100   = ["rsi", "stoch_k", "stoch_d", "mfi", "adx", "adx_plus", "adx_minus", "aroon_up", "aroon_down"]
BOUNDED_PM_100  = ["aroon_osc"]      # da -100..+100
BOUNDED_NEG_100 = ["williams_r"]     # da -100..0
# Pattern candele: bandierine 100/0/-100 → +1/0/-1
PATTERNS = [
    "cdl_doji", "cdl_hammer", "cdl_engulfing", "cdl_morning_star", "cdl_evening_star",
    "cdl_shooting_star", "cdl_hanging_man", "cdl_harami", "cdl_inverted_hammer",
]

# Ordine fisso delle feature nel tensore di ogni finestra.
FEATURE_COLS = (
    PRICE_GROUP + ["volume"] + UNBOUNDED
    + BOUNDED_0_100 + BOUNDED_PM_100 + BOUNDED_NEG_100 + PATTERNS
)

# Esclusi da questa prima versione perché pieni di NaN (uno attivo per volta o
# spostati nel tempo): psar_long/short/reversal, ichi_span_a/span_b/chikou.
# Si aggiungeranno quando gestiremo i loro NaN. (Filosofia: partire pulito.)

