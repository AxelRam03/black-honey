from dataclasses import dataclass


@dataclass
class RiskState:
    equity: float
    day_start_equity: float
    peak_equity: float
    halted: bool = False


class RiskManager:
    def __init__(self, risk_per_trade=0.0025, max_daily_loss=0.01, max_drawdown=0.03, max_position_fraction=0.25):
        self.risk_per_trade = risk_per_trade
        self.max_daily_loss = max_daily_loss
        self.max_drawdown = max_drawdown
        self.max_position_fraction = max_position_fraction

    def allowed(self, state: RiskState):
        if state.halted:
            return False, 'halted'
        if state.equity <= 0 or state.day_start_equity <= 0 or state.peak_equity <= 0:
            return False, 'invalid_equity'
        if state.equity <= state.day_start_equity * (1 - self.max_daily_loss):
            return False, 'daily_loss_limit'
        if state.equity <= state.peak_equity * (1 - self.max_drawdown):
            return False, 'drawdown_limit'
        return True, 'ok'

    def position_size(self, equity_quote: float, entry: float, stop: float) -> float:
        if equity_quote <= 0 or entry <= 0 or stop <= 0 or stop >= entry:
            return 0.0
        cash_risk = equity_quote * self.risk_per_trade
        qty_by_risk = cash_risk / (entry - stop)
        qty_by_cap = equity_quote * self.max_position_fraction / entry
        return max(0.0, min(qty_by_risk, qty_by_cap))
