import requests
from typing import List, Dict


class BinancePublic:
    def __init__(self, base_url: str = 'https://api.binance.com', timeout: int = 12):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()

    def klines(self, symbol: str, interval: str = '1h', limit: int = 200) -> List[Dict]:
        response = self.session.get(
            self.base_url + '/api/v3/klines',
            params={'symbol': symbol.upper(), 'interval': interval, 'limit': min(max(limit, 1), 1000)},
            timeout=self.timeout,
        )
        response.raise_for_status()
        rows = response.json()
        if not isinstance(rows, list):
            raise ValueError('Respuesta inesperada de Binance')
        # Excluir la última vela, que podría seguir abierta.
        rows = rows[:-1]
        return [{
            'open_time': int(row[0]), 'open': float(row[1]), 'high': float(row[2]),
            'low': float(row[3]), 'close': float(row[4]), 'volume': float(row[5]),
            'close_time': int(row[6])
        } for row in rows]
