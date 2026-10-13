import pytest

from app.backtest import run_backtest


def test_empty_backtest_preserves_starting_balance():
    result = run_backtest([], starting_balance=800, fee_rate=0.001)
    assert result["ending_balance"] == 800
    assert result["net_pnl"] == 0
    assert result["trades"] == []


def test_backtest_rejects_invalid_balance():
    with pytest.raises(ValueError):
        run_backtest([], starting_balance=0)


def test_backtest_rejects_invalid_fee():
    with pytest.raises(ValueError):
        run_backtest([], fee_rate=1)


def test_backtest_rejects_invalid_ohlc_values():
    candles = [{"open": 100, "high": 95, "low": 90, "close": 92}]
    with pytest.raises(ValueError, match="invalid OHLC"):
        run_backtest(candles)


def test_backtest_drawdown_includes_open_position_losses(monkeypatch):
    import app.backtest as backtest

    monkeypatch.setattr(
        backtest,
        "evaluate",
        lambda candles: {"signal": "LONG", "atr": 1.0, "price": 100.0},
    )
    candles = [
        {"open": 100.0, "high": 101.0, "low": 99.0, "close": 100.0}
        for _ in range(61)
    ]
    candles.append({"open": 100.0, "high": 100.5, "low": 98.5, "close": 99.0})
    result = run_backtest(candles, starting_balance=1000, fee_rate=0.001)
    assert result["max_drawdown_pct"] > 0
    assert result["trades"]
