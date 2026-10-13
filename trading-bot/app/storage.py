import sqlite3
import json
from datetime import datetime, timezone


class Store:
    def __init__(self, path='bot.sqlite3'):
        self.conn = sqlite3.connect(path)
        self.conn.execute('''CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL, symbol TEXT NOT NULL, event TEXT NOT NULL, payload TEXT NOT NULL
        )''')
        self.conn.commit()

    def log(self, symbol, event, payload):
        self.conn.execute(
            'INSERT INTO events(ts, symbol, event, payload) VALUES (?, ?, ?, ?)',
            (datetime.now(timezone.utc).isoformat(), symbol, event, json.dumps(payload, sort_keys=True))
        )
        self.conn.commit()

    def close(self):
        self.conn.close()
