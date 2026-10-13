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
        if quote_equity <= 0:
            raise ValueError("quote_equity debe ser mayor que cero")
        if not 0 <= fee_rate < 1:
            raise ValueError("fee_rate debe estar entre 0 y 1")
        self.quote_equity = float(quote_equity)
        self.fee_rate = float(fee_rate)
        self.position = None
        self.realized_pnl = 0.0

    def buy(self, symbol, qty, price, stop, target):
        if self.position or qty <= 0 or price <= 0:
            return False
        if stop <= 0 or stop >= price or target <= price:
            return False
        cost = qty * price * (1 + self.fee_rate)
        if cost > self.quote_equity:
            return False
        self.quote_equity -= cost
        self.position = PaperPosition(symbol.upper(), float(qty), float(price), float(stop), float(target))
        return True

    def mark(self, symbol, price, *, high=None, low=None, open_price=None):
        """Cierra solo la posición del símbolo correcto y evalúa el rango intravela.

        Si stop y objetivo se tocan en la misma vela, asume stop primero.
        """
        if not self.position or self.position.symbol != symbol.upper():
            return None
        if price <= 0:
            return None
        high = price if high is None else float(high)
        low = price if low is None else float(low)
        open_price = price if open_price is None else float(open_price)
        if low <= 0 or high < low or open_price <= 0:
            return None

        pos = self.position
        reason, fill_price = None, None
        if open_price <= pos.stop or low <= pos.stop:
            reason = 'stop'
            fill_price = min(open_price, pos.stop) if open_price <= pos.stop else pos.stop
        elif open_price >= pos.target or high >= pos.target:
            reason = 'target'
            fill_price = max(open_price, pos.target) if open_price >= pos.target else pos.target
        if reason is None:
            return None

        proceeds = pos.qty * fill_price * (1 - self.fee_rate)
        pnl = proceeds - pos.qty * pos.entry * (1 + self.fee_rate)
        self.quote_equity += proceeds
        self.realized_pnl += pnl
        self.position = None
        return {'symbol': pos.symbol, 'exit': reason, 'price': fill_price,
                'pnl': pnl, 'equity': self.quote_equity}
