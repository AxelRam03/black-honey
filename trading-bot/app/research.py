"""Paper-only parameter sensitivity experiment; not a live-trading component.

Compares a small, predeclared set of trend/momentum filters on the same recent
hourly candles. Results are exploratory and must not be used as proof of edge.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone

from . import backtest
from .indicators import atr, ema, rsi
from .market import BinancePublic


VARIANTS = [
    {"name": "baseline_20_50_rsi50_68", "fast": 20, "slow": 50, "rsi_min": 50, "rsi_max": 68},
    {"name": "trend_10_30_rsi50_65", "fast": 10, "slow": 30, "rsi_min": 50, "rsi_max": 65},
    {"name": "trend_20_50_rsi52_65", "fast": 20, "slow": 50, "rsi_min": 52, "rsi_max": 65},
    {"name": "trend_20_50_rsi55_70", "fast": 20, "slow": 50, "rsi_min": 55, "rsi_max": 70},
    {"name": "trend_12_40_rsi50_68", "fast": 12, "slow": 40, "rsi_min": 50, "rsi_max": 68},
]


def make_evaluator(config):
    def evaluate(candles):
        if len(candles) < max(60, config["slow"] + 2):
            return {"signal": "NONE", "reason": "insufficient_data"}
        closes = [float(c["close"]) for c in candles]
        fast = ema(closes, config["fast"])
        slow = ema(closes, config["slow"])
        momentum = rsi(closes, 14)
        volatility = atr(candles, 14)
        idx = len(candles) - 1
        vals = (fast[idx], slow[idx], momentum[idx], volatility[idx])
        if not all(math.isfinite(v) for v in vals):
            return {"signal": "NONE", "reason": "indicator_not_ready"}
        if (fast[idx] > slow[idx]
                and config["rsi_min"] <= momentum[idx] <= config["rsi_max"]
                and closes[idx] > fast[idx] and volatility[idx] > 0):
            return {"signal": "LONG", "reason": config["name"],
                    "price": closes[idx], "atr": volatility[idx]}
        return {"signal": "NONE", "reason": "no_setup", "price": closes[idx]}
    return evaluate


def main():
    symbols = [s.strip().upper() for s in __import__("os").getenv(
        "SYMBOLS", "BTCUSDT,ETHUSDT").split(",") if s.strip()]
    starting_balance = float(__import__("os").getenv("BACKTEST_STARTING_BALANCE", "1000"))
    fee_rate = float(__import__("os").getenv("FEE_RATE", "0.001"))
    api = BinancePublic(__import__("os").getenv(
        "BINANCE_BASE_URL", "https://data-api.binance.vision").rstrip("/"))
    original_evaluate = backtest.evaluate
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "paper_historical_parameter_sensitivity_only",
        "warning": "Recent sample only; not out-of-sample proof and not a trading recommendation.",
        "fee_rate_per_side": fee_rate,
        "starting_balance_per_symbol": starting_balance,
        "results": {},
    }
    try:
        for symbol in symbols:
            candles = api.klines(symbol, "1h", 1000)
            report["results"][symbol] = []
            for config in VARIANTS:
                backtest.evaluate = make_evaluator(config)
                metrics = backtest.run_backtest(candles, starting_balance, fee_rate)
                report["results"][symbol].append({
                    "variant": config["name"],
                    "fast_ema": config["fast"],
                    "slow_ema": config["slow"],
                    "rsi_min": config["rsi_min"],
                    "rsi_max": config["rsi_max"],
                    "return_pct": metrics["return_pct"],
                    "max_drawdown_pct": metrics["max_drawdown_pct"],
                    "trade_count": metrics["trade_count"],
                    "win_rate_pct": metrics["win_rate_pct"],
                    "profit_factor": metrics["profit_factor"],
                    "average_trade_pnl": metrics["average_trade_pnl"],
                })
    finally:
        backtest.evaluate = original_evaluate
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
