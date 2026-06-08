"""
Calcolo indicatori tecnici su un DataFrame di candele.
Chiamato da download_history.py su ogni batch prima del salvataggio in DB.
"""
import pandas as pd
import pandas_ta as ta

from config.settings import RSI_PERIOD, EMA_PERIODS, MACD_FAST, MACD_SLOW, MACD_SIGNAL, BB_PERIOD, BB_STD, ATR_PERIOD

# Nomi colonne BB generati da pandas-ta 0.4: BBL_20_2.0_2.0 (length_std_std)
_BB_COL = f"{BB_PERIOD}_{float(BB_STD):.1f}_{float(BB_STD):.1f}"


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Riceve un DataFrame con colonne OHLCV e aggiunge tutti gli indicatori.
    Restituisce il DataFrame arricchito, con NaN dove non ci sono abbastanza dati.
    """
    if df.empty or len(df) < 5:
        return df

    df = df.copy()

    # RSI
    df["rsi"] = ta.rsi(df["close"], length=RSI_PERIOD)

    # MACD
    macd = ta.macd(df["close"], fast=MACD_FAST, slow=MACD_SLOW, signal=MACD_SIGNAL)
    if macd is not None and not macd.empty:
        df["macd"]        = macd[f"MACD_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}"]
        df["macd_signal"] = macd[f"MACDs_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}"]
        df["macd_hist"]   = macd[f"MACDh_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}"]
    else:
        df["macd"] = df["macd_signal"] = df["macd_hist"] = None

    # EMA 20, 50, 200
    for period in EMA_PERIODS:
        df[f"ema_{period}"] = ta.ema(df["close"], length=period)

    # Bollinger Bands — pandas-ta 0.4 genera nomi tipo BBL_20_2.0_2.0
    bb = ta.bbands(df["close"], length=BB_PERIOD, std=BB_STD)
    if bb is not None and not bb.empty:
        df["bb_upper"] = bb.get(f"BBU_{_BB_COL}", bb.filter(like="BBU").iloc[:, 0] if bb.filter(like="BBU").shape[1] else None)
        df["bb_mid"]   = bb.get(f"BBM_{_BB_COL}", bb.filter(like="BBM").iloc[:, 0] if bb.filter(like="BBM").shape[1] else None)
        df["bb_lower"] = bb.get(f"BBL_{_BB_COL}", bb.filter(like="BBL").iloc[:, 0] if bb.filter(like="BBL").shape[1] else None)
    else:
        df["bb_upper"] = df["bb_mid"] = df["bb_lower"] = None

    # ATR
    df["atr"] = ta.atr(df["high"], df["low"], df["close"], length=ATR_PERIOD)

    # Pattern candele — solo doji disponibile senza TA-Lib
    # hammer, engulfing, morning/evening star richiedono: brew install ta-lib && pip install TA-Lib
    cdl = ta.cdl_pattern(df["open"], df["high"], df["low"], df["close"], name=["doji"])
    if cdl is not None and not cdl.empty and "CDL_DOJI_10_0.1" in cdl.columns:
        df["cdl_doji"] = cdl["CDL_DOJI_10_0.1"].fillna(0).astype("int64")
    else:
        df["cdl_doji"] = 0

    for col in ["cdl_hammer", "cdl_engulfing", "cdl_morning_star", "cdl_evening_star"]:
        df[col] = 0  # placeholder — si attivano dopo brew install ta-lib

    return df
