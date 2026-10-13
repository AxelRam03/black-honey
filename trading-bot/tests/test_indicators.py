from app.indicators import rsi, ema, atr


def test_rsi_is_neutral_for_flat_prices():
    values = rsi([100.0] * 20, period=14)
    assert values[14] == 50.0
    assert values[-1] == 50.0


def test_rsi_is_100_for_strictly_rising_prices():
    values = rsi([float(i) for i in range(20)], period=14)
    assert values[14] == 100.0
    assert values[-1] == 100.0


def test_ema_returns_empty_for_insufficient_data():
    assert ema([1.0, 2.0], period=3) == []


def test_atr_returns_empty_for_insufficient_data():
    assert atr([{"open": 1, "high": 1, "low": 1, "close": 1}] * 5, period=14) == []
