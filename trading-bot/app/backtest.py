from __future__ import annotations

from typing import Any

from .risk import RiskManager, RiskState
from .strategy import evaluate


def run_backtest(
    candles: list[dict[str, Any]],
    starting_balance: float = 1000.0,
    fee_rate: float = 0.001,
) -> dict[str, Any]:
    """Run a conservative, long-only candle backtest without network/API access.

    Signals are calculated from candles strictly before the current candle; entries
    occur at the current candle open. If stop and target are both touched in one
    candle, the stop is assumed to have filled first. This is a rough research tool,
    not a realistic exchange execution simulator.
    """
    if starting_balance <= 0:
        raise ValueError("starting_balance must be positive")
    if not 0 <= fee_rate < 1:
        raise ValueError("fee_rate must be between 0 and 1")
    if not candles:
        return {
            "starting_balance": starting_balance,
            "ending_balance": starting_balance,
            "net_pnl": 0.0,
            "return_pct": 0.0,
            "max_drawdown_pct": 0.0,
            "trades": [],
        }

    balance = float(starting_balance)
    peak = balance
    max_drawdown = 0.0
    position = None
    trades = []

    def close_position(exit_price: float, reason: str) -> None:
        nonlocal balance, position
        pos = position
        exit_value = pos["qty"] * exit_price
        entry_value = pos["qty"] * pos["entry"]
        fees = (entry_value + exit_value) * fee_rate
        pnl = exit_value - entry_value - fees
        balance += pnl
        trades.append({
            "entry": pos["entry"],
            "exit": float(exit_price),
            "qty": pos["qty"],
            "reason": reason,
            "pnl": pnl,
            "balance": balance,
        })
        position = None

    for i, candle in enumerate(candles):
        high = float(candle["high"])
        low = float(candle["low"])
        open_price = float(candle.get("open", candle["close"]))
        close_price = float(candle["close"])

        if position is not None:
            stop_hit = low <= position["stop"]
            target_hit = high >= position["target"]
            if stop_hit:
                close_position(position["stop"], "stop")
            elif target_hit:
                close_position(position["target"], "target")

        if position is None and i >= 60:
            signal = evaluate(candles[:i])
            if signal.get("signal") == "LONG":
                entry = open_price
                atr_value = float(signal["atr"])
                stop = entry - 2.0 * atr_value
                if stop > 0 and stop < entry:
                    risk = RiskManager()
                    state = RiskState(balance, balance, max(peak, balance))
                    allowed, _ = risk.allowed(state)
                    qty = risk.position_size(balance, entry, stop)
                    qty = min(qty, balance / (entry * (1 + fee_rate)))
                    if allowed and qty > 0:
                        target = entry + 2.0 * (entry - stop)
                        position = {
                            "entry": entry,
                            "stop": stop,
                            "target": target,
                            "qty": qty,
                        }

        if balance > peak:
            peak = balance
        if peak > 0:
            max_drawdown = max(max_drawdown, (peak - balance) / peak)

    if position is not None:
        close_position(float(candles[-1]["close"]), "end_of_data")
        if balance > peak:
            peak = balance
        if peak > 0:
            max_drawdown = max(max_drawdown, (peak - balance) / peak)

    net_pnl = balance - starting_balance
    return {
        "starting_balance": float(starting_balance),
        "ending_balance": balance,
        "net_pnl": net_pnl,
        "return_pct": net_pnl / starting_balance * 100,
        "max_drawdown_pct": max_drawdown * 100,
        "trades": trades,
    }
