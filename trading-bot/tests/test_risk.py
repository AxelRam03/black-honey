from app.risk import RiskManager, RiskState


def test_position_size_respects_risk_and_cap():
    manager = RiskManager(risk_per_trade=0.0025, max_position_fraction=0.25)
    qty = manager.position_size(1000, 100, 95)
    assert qty > 0
    assert qty * (100 - 95) <= 1000 * 0.0025 + 1e-9
    assert qty * 100 <= 1000 * 0.25 + 1e-9


def test_daily_loss_limit_blocks():
    manager = RiskManager(max_daily_loss=0.01)
    allowed, reason = manager.allowed(RiskState(989, 1000, 1000))
    assert not allowed and reason == 'daily_loss_limit'


def test_drawdown_limit_blocks_independently_of_daily_loss():
    manager = RiskManager(max_daily_loss=0.01, max_drawdown=0.03)
    allowed, reason = manager.allowed(RiskState(969, 950, 1000))
    assert not allowed and reason == 'drawdown_limit'


def test_halted_state_blocks():
    manager = RiskManager()
    state = RiskState(1000, 1000, 1000, halted=True)
    assert manager.allowed(state) == (False, 'halted')


from app.paper import PaperBroker


def test_paper_buy_deducts_cost_and_entry_fee():
    broker = PaperBroker(quote_equity=100.0, fee_rate=0.001)
    assert broker.buy("BTCUSDT", 0.5, 100.0, 90.0, 120.0)
    assert abs(broker.quote_equity - 49.95) < 1e-9
    assert broker.position.symbol == "BTCUSDT"


def test_paper_buy_rejects_position_that_exceeds_cash_including_fee():
    broker = PaperBroker(quote_equity=100.0, fee_rate=0.001)
    assert not broker.buy("BTCUSDT", 1.0, 100.0, 90.0, 120.0)
    assert broker.position is None
    assert broker.quote_equity == 100.0


def test_paper_mark_ignores_other_symbols():
    broker = PaperBroker(quote_equity=100.0)
    assert broker.buy("BTCUSDT", 0.2, 100.0, 90.0, 120.0)
    assert broker.mark("ETHUSDT", 80.0, low=70.0, high=130.0) is None
    assert broker.position is not None


def test_paper_stop_wins_when_stop_and_target_touch_same_candle():
    broker = PaperBroker(quote_equity=100.0, fee_rate=0.001)
    assert broker.buy("BTCUSDT", 0.2, 100.0, 90.0, 120.0)
    event = broker.mark("BTCUSDT", 100.0, open_price=100.0, low=85.0, high=125.0)
    assert event["exit"] == "stop"
    assert event["price"] == 90.0
    assert broker.position is None


def test_paper_gap_through_stop_fills_at_open_not_stop():
    broker = PaperBroker(quote_equity=100.0, fee_rate=0.001)
    assert broker.buy("BTCUSDT", 0.2, 100.0, 90.0, 120.0)
    event = broker.mark("BTCUSDT", 85.0, open_price=85.0, low=80.0, high=95.0)
    assert event["exit"] == "stop"
    assert event["price"] == 85.0


def test_paper_target_gap_fills_at_open_and_updates_realized_pnl():
    broker = PaperBroker(quote_equity=100.0, fee_rate=0.001)
    assert broker.buy("BTCUSDT", 0.2, 100.0, 90.0, 120.0)
    event = broker.mark("BTCUSDT", 125.0, open_price=125.0, low=121.0, high=130.0)
    assert event["exit"] == "target"
    assert event["price"] == 125.0
    assert event["pnl"] > 0
    assert broker.realized_pnl == event["pnl"]
