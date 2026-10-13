import os
import re
from dataclasses import dataclass
from urllib.parse import urlsplit

from dotenv import load_dotenv

load_dotenv()

_ALLOWED_HOSTS = {"data-api.binance.vision", "api.binance.com"}
_SYMBOL_RE = re.compile(r"^[A-Z0-9]{5,20}$")


def _float(name, default):
    try:
        return float(os.getenv(name, str(default)))
    except ValueError as exc:
        raise ValueError(f"{name} debe ser numérico") from exc


@dataclass(frozen=True)
class Config:
    base_url: str = os.getenv("BINANCE_BASE_URL", "https://data-api.binance.vision").rstrip("/")
    symbols: tuple = tuple(s.strip().upper() for s in os.getenv("SYMBOLS", "BTCUSDT,ETHUSDT").split(",") if s.strip())
    interval: str = os.getenv("INTERVAL", "1h")
    poll_seconds: int = int(os.getenv("POLL_SECONDS", "60"))
    paper_quote_balance: float = _float("PAPER_QUOTE_BALANCE", 100.0)
    risk_per_trade: float = _float("RISK_PER_TRADE", 0.0025)
    max_daily_loss: float = _float("MAX_DAILY_LOSS", 0.01)
    max_drawdown: float = _float("MAX_DRAWDOWN", 0.03)
    max_position_fraction: float = _float("MAX_POSITION_FRACTION", 0.25)
    stop_atr_multiple: float = _float("STOP_ATR_MULTIPLE", 2.0)
    take_profit_r_multiple: float = _float("TAKE_PROFIT_R_MULTIPLE", 2.0)
    fee_rate: float = _float("FEE_RATE", 0.001)
    db_path: str = os.getenv("DB_PATH", "bot.sqlite3")

    def validate(self):
        if self.interval != "1h":
            raise ValueError("Esta versión está diseñada para velas 1h.")
        if not self.symbols:
            raise ValueError("Define al menos un símbolo.")
        if any(not _SYMBOL_RE.fullmatch(symbol) for symbol in self.symbols):
            raise ValueError("SYMBOLS contiene un símbolo con formato inválido.")
        if len(set(self.symbols)) != len(self.symbols):
            raise ValueError("SYMBOLS no debe contener símbolos duplicados.")
        if not 0 < self.risk_per_trade <= 0.01:
            raise ValueError("RISK_PER_TRADE debe estar entre 0 y 1%.")
        if not 0 < self.max_daily_loss <= 0.03:
            raise ValueError("MAX_DAILY_LOSS debe estar entre 0 y 3%.")
        if not 0 < self.max_drawdown <= 0.10:
            raise ValueError("MAX_DRAWDOWN debe estar entre 0 y 10%.")
        if not 0 < self.max_position_fraction <= 0.25:
            raise ValueError("MAX_POSITION_FRACTION debe estar entre 0 y 25%.")
        if self.paper_quote_balance <= 0:
            raise ValueError("PAPER_QUOTE_BALANCE debe ser mayor que cero.")
        if not 0 <= self.fee_rate < 1:
            raise ValueError("FEE_RATE debe estar entre 0 y 1.")
        if self.poll_seconds < 10:
            raise ValueError("POLL_SECONDS no puede ser menor que 10.")
        if self.stop_atr_multiple <= 0 or self.take_profit_r_multiple <= 0:
            raise ValueError("Los múltiplos de stop y objetivo deben ser positivos.")
        parsed = urlsplit(self.base_url)
        if (parsed.scheme != "https" or parsed.hostname not in _ALLOWED_HOSTS
                or parsed.username is not None or parsed.password is not None
                or parsed.port not in (None, 443) or parsed.path not in ("", "/")\n                or parsed.query or parsed.fragment):
            raise ValueError("BINANCE_BASE_URL debe usar un host HTTPS oficial permitido.")
