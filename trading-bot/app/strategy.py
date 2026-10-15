import math
from .indicators import ema, rsi, atr


def evaluate(candles):
    """Señal experimental: tendencia e impulso usando solamente velas cerradas."""
    if len(candles) < 60:
        return {'signal': 'NONE', 'reason': 'insufficient_data'}
    closes = [float(c['close']) for c in candles]
    e20, e50 = ema(closes, 20), ema(closes, 50)
    r14, a14 = rsi(closes, 14), atr(candles, 14)
    idx = len(candles) - 1
    values = [e20[idx], e50[idx], r14[idx], a14[idx]]
    if not all(math.isfinite(value) for value in values):
        return {'signal': 'NONE', 'reason': 'indicator_not_ready'}
    if e20[idx] > e50[idx] and 50 <= r14[idx] <= 68 and closes[idx] > e20[idx] and a14[idx] > 0:
        return {'signal': 'LONG', 'reason': 'trend_momentum_confirmed', 'price': closes[idx], 'atr': a14[idx]}
    return {'signal': 'NONE', 'reason': 'no_setup', 'price': closes[idx]}
