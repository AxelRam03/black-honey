from app.strategy import evaluate


def test_requires_enough_candles():
    assert evaluate([])['signal'] == 'NONE'
    assert evaluate([{'close': 1, 'high': 1, 'low': 1}] * 20)['signal'] == 'NONE'


def test_bad_candle_count_does_not_trigger_entry():
    candles = [{'close': 100 + i, 'high': 101 + i, 'low': 99 + i} for i in range(55)]
    assert evaluate(candles)['signal'] == 'NONE'
