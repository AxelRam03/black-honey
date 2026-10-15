import math
from typing import List, Dict


def ema(values: List[float], period: int) -> List[float]:
    if period <= 0 or len(values) < period:
        return []
    alpha = 2 / (period + 1)
    result = [float('nan')] * (period - 1)
    current = sum(values[:period]) / period
    result.append(current)
    for value in values[period:]:
        current = alpha * value + (1 - alpha) * current
        result.append(current)
    return result


def rsi(values: List[float], period: int = 14) -> List[float]:
    if period <= 0 or len(values) <= period:
        return []
    deltas = [values[i] - values[i - 1] for i in range(1, len(values))]
    gains = [max(x, 0.0) for x in deltas]
    losses = [max(-x, 0.0) for x in deltas]
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    out = [float('nan')] * period
    out.append(100.0 if avg_loss == 0 and avg_gain > 0 else 50.0 if avg_gain == 0 else 100 - 100 / (1 + avg_gain / avg_loss))
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        out.append(50.0 if avg_loss == 0 and avg_gain == 0 else 100.0 if avg_loss == 0 else 100 - 100 / (1 + avg_gain / avg_loss))
    return out


def atr(candles: List[Dict], period: int = 14) -> List[float]:
    if period <= 0 or len(candles) <= period:
        return []
    trs = []
    for i, candle in enumerate(candles):
        high, low = float(candle['high']), float(candle['low'])
        previous_close = float(candles[i - 1]['close']) if i else float(candle['close'])
        trs.append(max(high - low, abs(high - previous_close), abs(low - previous_close)))
    out = [float('nan')] * period
    current = sum(trs[1:period + 1]) / period
    out.append(current)
    for tr in trs[period + 1:]:
        current = (current * (period - 1) + tr) / period
        out.append(current)
    return out
