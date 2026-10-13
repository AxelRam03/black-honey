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
