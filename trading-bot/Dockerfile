FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    DB_PATH=/var/data/bot.sqlite3 \
    PAPER_QUOTE_BALANCE=100 \
    SYMBOLS=BTCUSDT,ETHUSDT \
    BINANCE_BASE_URL=https://data-api.binance.vision \
    POLL_SECONDS=60 \
    FEE_RATE=0.001 \
    RISK_PER_TRADE=0.001 \
    MAX_DAILY_LOSS=0.005 \
    MAX_DRAWDOWN=0.02 \
    MAX_POSITION_FRACTION=0.10

WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY app ./app

RUN useradd --create-home --uid 10001 botuser \
    && mkdir -p /var/data \
    && chown -R botuser:botuser /app /var/data

USER botuser
VOLUME ["/var/data"]
CMD ["python", "-m", "app.main"]
