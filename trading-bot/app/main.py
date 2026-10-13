import logging
import time
from .config import Config
from .market import BinancePublic
from .strategy import evaluate
from .risk import RiskManager, RiskState
from .storage import Store
from .paper import PaperBroker

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')


def run():
    cfg = Config()
    cfg.validate()
    api = BinancePublic(cfg.base_url)
    store = Store(cfg.db_path)
    broker = PaperBroker(quote_equity=cfg.paper_quote_balance, fee_rate=cfg.fee_rate)
    state = RiskState(equity=broker.quote_equity, day_start_equity=broker.quote_equity, peak_equity=broker.quote_equity)
    risk = RiskManager(cfg.risk_per_trade, cfg.max_daily_loss, cfg.max_drawdown, cfg.max_position_fraction)
    last_candle = {}
    logging.info('PAPER MODE: no se envían órdenes reales ni se usan claves privadas.')
    try:
        while True:
            for symbol in cfg.symbols:
                try:
                    candles = api.klines(symbol, cfg.interval, 200)
                    if not candles:
                        continue
                    candle_id = candles[-1]['close_time']
                    if last_candle.get(symbol) == candle_id:
                        continue
                    last_candle[symbol] = candle_id
                    signal = evaluate(candles)
                    price = candles[-1]['close']
                    exit_event = broker.mark(price)
                    if exit_event:
                        state.equity = broker.quote_equity
                        state.peak_equity = max(state.peak_equity, state.equity)
                        store.log(symbol, 'paper_exit', exit_event)
                        logging.info('%s salida simulada: %s', symbol, exit_event)
                    allowed, reason = risk.allowed(state)
                    store.log(symbol, 'signal', {'signal': signal, 'risk_allowed': allowed, 'risk_reason': reason})
                    if signal.get('signal') == 'LONG' and allowed and broker.position is None:
                        entry = signal['price']
                        stop = entry - cfg.stop_atr_multiple * signal['atr']
                        target = entry + cfg.take_profit_r_multiple * (entry - stop)
                        qty = risk.position_size(broker.quote_equity, entry, stop)
                        if qty > 0 and broker.buy(symbol, qty, entry, stop, target):
                            payload = {'qty': qty, 'entry': entry, 'stop': stop, 'target': target}
                            store.log(symbol, 'paper_entry', payload)
                            logging.info('%s compra simulada: %s', symbol, payload)
                except Exception as exc:
                    logging.exception('Error procesando %s', symbol)
                    store.log(symbol, 'error', {'error': str(exc)})
            time.sleep(max(10, cfg.poll_seconds))
    except KeyboardInterrupt:
        logging.info('Detenido por el usuario.')
    finally:
        store.close()


if __name__ == '__main__':
    run()
