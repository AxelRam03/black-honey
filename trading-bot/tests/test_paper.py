from app.paper import PaperBroker


def test_buy_and_target_exit_updates_balance_after_fees():
    broker = PaperBroker(quote_equity=1000, fee_rate=0.001)
    assert broker.buy('BTCUSDT', 1, 100, 90, 120)
    assert broker.position is not None
    event = broker.mark('BTCUSDT', 120)
    assert event['exit'] == 'target'
    assert event['pnl'] < 20  # entry and exit fees are included
    assert broker.position is None
    assert broker.quote_equity > 1000


def test_buy_rejects_position_that_exceeds_cash():
    broker = PaperBroker(quote_equity=100, fee_rate=0.001)
    assert not broker.buy('BTCUSDT', 2, 100, 90, 120)
    assert broker.position is None


def test_stop_exit_updates_balance_and_clears_position():
    broker = PaperBroker(quote_equity=1000, fee_rate=0.001)
    assert broker.buy('BTCUSDT', 1, 100, 90, 120)
    event = broker.mark('BTCUSDT', 89)
    assert event['exit'] == 'stop'
    assert event['pnl'] < 0
    assert broker.position is None


def test_price_from_another_symbol_cannot_close_position():
    broker = PaperBroker(quote_equity=1000, fee_rate=0.001)
    assert broker.buy('BTCUSDT', 0.01, 100, 90, 120)
    event = broker.mark('ETHUSDT', 120)
    assert event is None
    assert broker.position is not None


def test_buy_rejects_invalid_stop_or_target():
    broker = PaperBroker(quote_equity=1000)
    assert not broker.buy('BTCUSDT', 1, 100, 100, 120)
    assert not broker.buy('BTCUSDT', 1, 100, 90, 100)
    assert broker.position is None


def test_broker_rejects_invalid_balance_or_fee():
    import pytest
    with pytest.raises(ValueError):
        PaperBroker(quote_equity=0)
    with pytest.raises(ValueError):
        PaperBroker(fee_rate=1)
