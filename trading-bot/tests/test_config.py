import pytest

from app.config import Config


def test_default_configuration_is_valid():
    Config().validate()


@pytest.mark.parametrize(
    "url",
    [
        "http://api.binance.com",
        "https://data-api.binance.vision.evil.example",
        "https://api.binance.com.evil.example",
        "https://user:pass@api.binance.com",
        "https://api.binance.com:444",
        "https://api.binance.com/path",
    ],
)
def test_rejects_untrusted_or_malformed_api_endpoint(url):
    with pytest.raises(ValueError, match="BINANCE_BASE_URL"):
        Config(base_url=url).validate()


@pytest.mark.parametrize("url", ["https://api.binance.com", "https://data-api.binance.vision"])
def test_accepts_official_https_endpoints(url):
    Config(base_url=url).validate()


@pytest.mark.parametrize("symbols", [(), ("BTCUSDT", "BTCUSDT"), ("BTC/USDT",), ("BTC USDT",)])
def test_rejects_invalid_or_duplicate_symbols(symbols):
    with pytest.raises(ValueError):
        Config(symbols=symbols).validate()


def test_rejects_polling_interval_below_minimum():
    with pytest.raises(ValueError, match="POLL_SECONDS"):
        Config(poll_seconds=9).validate()


def test_rejects_risk_above_limit():
    with pytest.raises(ValueError, match="RISK_PER_TRADE"):
        Config(risk_per_trade=0.02).validate()
