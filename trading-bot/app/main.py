import logging
import time
from datetime import datetime, timezone
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
    last_prices = {}
    current_day = None
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
                    candle = candles[-1]
                    price = candle['close']
                    last_prices[symbol] = price
                    day = datetime.fromtimestamp(candle['close_time'] / 1000, tz=timezone.utc).date()
                    if current_day != day:
                        current_day = day
                        state.day_start_equity = state.equity

                    signal = evaluate(candles)
                    exit_event = broker.mark(symbol, price)
                    if exit_event:
                        store.log(symbol, 'paper_exit', exit_event)
                        logging.info('%s salida simulada: %s', symbol, exit_event)

                    # Patrimonio simulado = efectivo disponible + valor de mercado de la posición abierta.
                    state.equity = broker.quote_equity
                    if broker.position:
                        position_price = last_prices.get(broker.position.symbol, broker.position.entry)
                        state.equity += broker.position.qty * position_price
                    state.peak_equity = max(state.peak_equity, state.equity)

                    allowed, reason = risk.allowed(state)
                    store.log(symbol, 'signal', {'signal': signal, 'risk_allowed': allowed, 'risk_reason': reason})
                    if signal.get('signal') == 'LONG' and allowed and broker.position is None:
                        entry = signal['price']
                        stop = entry - cfg.stop_atr_multiple * signal['atr']
                        target = entry + cfg.take_profit_r_multiple * (entry - stop)
                        qty = risk.position_size(state.equity, entry, stop)
                        if qty > 0 and broker.buy(symbol, qty, entry, stop, target):
                            payload = {'qty': qty, 'entry': entry, 'stop': stop, 'target': target}
                            store.log(symbol, 'paper_entry', payload)
                            logging.info('%s compra simulada: %s', symbol, payload)
                            state.equity = broker.quote_equity + qty * entry
                            state.peak_equity = max(state.peak_equity, state.equity)
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
