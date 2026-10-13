from dataclasses import dataclass


@dataclass
class PaperPosition:
    symbol: str
    qty: float
    entry: float
    stop: float
    target: float


class PaperBroker:
    """Simulador simple; no representa liquidez, latencia ni ejecuciones parciales reales."""
    def __init__(self, quote_equity=100.0, fee_rate=0.001):
        self.quote_equity = float(quote_equity)
        self.fee_rate = float(fee_rate)
        self.position = None
        self.realized_pnl = 0.0

    def buy(self, symbol, qty, price, stop, target):
        if self.position or qty <= 0 or price <= 0:
            return False
        cost = qty * price * (1 + self.fee_rate)
        if cost > self.quote_equity:
            return False
        self.quote_equity -= cost
        self.position = PaperPosition(symbol, qty, price, stop, target)
        return True

    def mark(self, price):
        if not self.position:
            return None
        pos = self.position
        reason = 'stop' if price <= pos.stop else 'target' if price >= pos.target else None
        if reason is None:
            return None
        proceeds = pos.qty * price * (1 - self.fee_rate)
        pnl = proceeds - pos.qty * pos.entry * (1 + self.fee_rate)
        self.quote_equity += proceeds
        self.realized_pnl += pnl
        self.position = None
        return {'exit': reason, 'price': price, 'pnl': pnl, 'equity': self.quote_equity}
