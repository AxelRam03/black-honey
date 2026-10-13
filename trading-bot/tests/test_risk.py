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


def test_drawdown_limit_blocks():
    manager = RiskManager(max_drawdown=0.03)
    allowed, reason = manager.allowed(RiskState(969, 1000, 1000))
    assert not allowed and reason == 'drawdown_limit'


def test_halted_state_blocks():
    manager = RiskManager()
    state = RiskState(1000, 1000, 1000, halted=True)
    assert manager.allowed(state) == (False, 'halted')
