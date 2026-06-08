SELECT ts, open, high, low, close, volume,
       rsi, macd, ema_20, ema_50, ema_200,
       bb_upper, bb_lower, atr
FROM candles
WHERE ticker = 'AAPL'
ORDER BY ts DESC
LIMIT 5;