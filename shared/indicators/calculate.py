"""
Calcolo indicatori tecnici su un DataFrame di candele.
Chiamato da download_history.py su ogni batch e da recalculate_indicators.py.

Colonne prodotte (45 indicatori + pattern):
  Momentum  : rsi, stoch_k, stoch_d, roc, williams_r, cci
  Trend dir : macd, macd_signal, macd_hist, ema_20/50/200,
              psar_long, psar_short, psar_reversal, aroon_up, aroon_down, aroon_osc
  Trend str : adx, adx_plus, adx_minus
  Volatilità: bb_upper, bb_mid, bb_lower, atr, dc_upper, dc_lower, kc_upper, kc_lower
  Volume    : obv, mfi, cmf, force_index
  Ichimoku  : ichi_tenkan, ichi_kijun, ichi_span_a, ichi_span_b, ichi_chikou
  Pattern   : cdl_doji, cdl_hammer, cdl_engulfing, cdl_morning_star, cdl_evening_star,
              cdl_shooting_star, cdl_hanging_man, cdl_harami, cdl_inverted_hammer
"""
import pandas as pd
import pandas_ta as ta

from shared.config.settings import (
    RSI_PERIOD, EMA_PERIODS, MACD_FAST, MACD_SLOW, MACD_SIGNAL,
    BB_PERIOD, BB_STD, ATR_PERIOD,
)

_BB_COL = f"{BB_PERIOD}_{float(BB_STD):.1f}_{float(BB_STD):.1f}"

_CDL_PATTERNS = [
    ("cdl_doji",            "doji",           "CDL_DOJI_10_0.1"),
    ("cdl_hammer",          "hammer",          "CDL_HAMMER"),
    ("cdl_engulfing",       "engulfing",       "CDL_ENGULFING"),
    ("cdl_morning_star",    "morningstar",     "CDL_MORNINGSTAR"),
    ("cdl_evening_star",    "eveningstar",     "CDL_EVENINGSTAR"),
    ("cdl_shooting_star",   "shootingstar",    "CDL_SHOOTINGSTAR"),
    ("cdl_hanging_man",     "hangingman",      "CDL_HANGINGMAN"),
    ("cdl_harami",          "harami",          "CDL_HARAMI"),
    ("cdl_inverted_hammer", "invertedhammer",  "CDL_INVERTEDHAMMER"),
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Riceve un DataFrame con colonne OHLCV e aggiunge tutti gli indicatori.
    Restituisce il DataFrame arricchito (NaN dove i dati non bastano).
    """
    if df.empty or len(df) < 5:
        return df

    df = df.copy()
    o, h, l, c, v = df["open"], df["high"], df["low"], df["close"], df["volume"]

    # ── Momentum ────────────────────────────────────────────────────────────
    df["rsi"] = ta.rsi(c, length=RSI_PERIOD)

    stoch = ta.stoch(h, l, c)
    df["stoch_k"] = stoch.get("STOCHk_14_3_3") if stoch is not None else None
    df["stoch_d"] = stoch.get("STOCHd_14_3_3") if stoch is not None else None

    df["roc"]       = ta.roc(c, length=10)
    df["williams_r"]= ta.willr(h, l, c, length=14)
    df["cci"]       = ta.cci(h, l, c, length=14)

    # ── Trend — direzione ───────────────────────────────────────────────────
    macd = ta.macd(c, fast=MACD_FAST, slow=MACD_SLOW, signal=MACD_SIGNAL)
    if macd is not None and not macd.empty:
        df["macd"]        = macd.get(f"MACD_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}")
        df["macd_signal"] = macd.get(f"MACDs_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}")
        df["macd_hist"]   = macd.get(f"MACDh_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}")
    else:
        df["macd"] = df["macd_signal"] = df["macd_hist"] = None

    for period in EMA_PERIODS:
        df[f"ema_{period}"] = ta.ema(c, length=period)

    psar = ta.psar(h, l, c)
    if psar is not None and not psar.empty:
        df["psar_long"]     = psar.get("PSARl_0.02_0.2")
        df["psar_short"]    = psar.get("PSARs_0.02_0.2")
        psar_r              = psar.get("PSARr_0.02_0.2")
        df["psar_reversal"] = psar_r.fillna(0).astype("int64") if psar_r is not None else 0
    else:
        df["psar_long"] = df["psar_short"] = None
        df["psar_reversal"] = 0

    aroon = ta.aroon(h, l, length=25)
    if aroon is not None and not aroon.empty:
        df["aroon_up"]  = aroon.get("AROONU_25")
        df["aroon_down"]= aroon.get("AROOND_25")
        df["aroon_osc"] = aroon.get("AROONOSC_25")
    else:
        df["aroon_up"] = df["aroon_down"] = df["aroon_osc"] = None

    # ── Trend — forza ───────────────────────────────────────────────────────
    adx = ta.adx(h, l, c, length=14)
    if adx is not None and not adx.empty:
        df["adx"]       = adx.get("ADX_14")
        df["adx_plus"]  = adx.get("DMP_14")
        df["adx_minus"] = adx.get("DMN_14")
    else:
        df["adx"] = df["adx_plus"] = df["adx_minus"] = None

    # ── Volatilità ──────────────────────────────────────────────────────────
    bb = ta.bbands(c, length=BB_PERIOD, std=BB_STD)
    if bb is not None and not bb.empty:
        df["bb_upper"] = bb.get(f"BBU_{_BB_COL}", bb.filter(like="BBU").iloc[:, 0] if bb.filter(like="BBU").shape[1] else None)
        df["bb_mid"]   = bb.get(f"BBM_{_BB_COL}", bb.filter(like="BBM").iloc[:, 0] if bb.filter(like="BBM").shape[1] else None)
        df["bb_lower"] = bb.get(f"BBL_{_BB_COL}", bb.filter(like="BBL").iloc[:, 0] if bb.filter(like="BBL").shape[1] else None)
    else:
        df["bb_upper"] = df["bb_mid"] = df["bb_lower"] = None

    df["atr"] = ta.atr(h, l, c, length=ATR_PERIOD)

    dc = ta.donchian(h, l, length=20)
    if dc is not None and not dc.empty:
        df["dc_upper"] = dc.get("DCU_20_20")
        df["dc_lower"] = dc.get("DCL_20_20")
    else:
        df["dc_upper"] = df["dc_lower"] = None

    kc = ta.kc(h, l, c, length=20)
    if kc is not None and not kc.empty:
        df["kc_upper"] = kc.get("KCUe_20_2")
        df["kc_lower"] = kc.get("KCLe_20_2")
    else:
        df["kc_upper"] = df["kc_lower"] = None

    # ── Volume ──────────────────────────────────────────────────────────────
    df["obv"]         = ta.obv(c, v)
    df["mfi"]         = ta.mfi(h, l, c, v, length=14)
    df["cmf"]         = ta.cmf(h, l, c, v, length=20)
    df["force_index"] = ta.efi(c, v, length=13)

    # ── Ichimoku ────────────────────────────────────────────────────────────
    ichi_result = ta.ichimoku(h, l, c)
    if ichi_result is not None:
        ichi_df = ichi_result[0] if isinstance(ichi_result, tuple) else ichi_result
        if ichi_df is not None and not ichi_df.empty:
            df["ichi_tenkan"] = ichi_df.get("ITS_9")
            df["ichi_kijun"]  = ichi_df.get("IKS_26")
            df["ichi_span_a"] = ichi_df.get("ISA_9")
            df["ichi_span_b"] = ichi_df.get("ISB_26")
            df["ichi_chikou"] = ichi_df.get("ICS_26")
        else:
            df["ichi_tenkan"] = df["ichi_kijun"] = df["ichi_span_a"] = df["ichi_span_b"] = df["ichi_chikou"] = None
    else:
        df["ichi_tenkan"] = df["ichi_kijun"] = df["ichi_span_a"] = df["ichi_span_b"] = df["ichi_chikou"] = None

    # ── Pattern candele ─────────────────────────────────────────────────────
    for col, pattern_name, cdl_col in _CDL_PATTERNS:
        try:
            cdl = ta.cdl_pattern(o, h, l, c, name=[pattern_name])
            if cdl is not None and not cdl.empty and cdl_col in cdl.columns:
                df[col] = cdl[cdl_col].fillna(0).astype("int64")
            else:
                df[col] = 0
        except Exception:
            df[col] = 0

    return df
