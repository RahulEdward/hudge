"""Tick data persistence — stores raw ticks, supports replay and aggregation."""

import os
import time
from typing import List, Dict, Any, Optional
from loguru import logger

_storage = None
DB_PATH = "database/tick_data.db"


class TickStorage:
    """Store raw tick data to SQLite for replay and OHLCV aggregation."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._conn = None
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

    def _get_conn(self):
        if self._conn is None:
            import sqlite3
            self._conn = sqlite3.connect(self.db_path)
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS ticks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    exchange TEXT DEFAULT 'NSE',
                    ltp REAL NOT NULL,
                    volume INTEGER DEFAULT 0,
                    bid REAL DEFAULT 0,
                    ask REAL DEFAULT 0,
                    timestamp REAL NOT NULL,
                    received_at REAL NOT NULL
                )
            """)
            self._conn.execute("CREATE INDEX IF NOT EXISTS idx_ticks_symbol_ts ON ticks(symbol, timestamp)")
            self._conn.commit()
        return self._conn

    async def store_tick(self, tick: Dict[str, Any]):
        """Store a single tick."""
        conn = self._get_conn()
        conn.execute(
            "INSERT INTO ticks (symbol, exchange, ltp, volume, bid, ask, timestamp, received_at) VALUES (?,?,?,?,?,?,?,?)",
            (
                tick.get("symbol", ""),
                tick.get("exchange", "NSE"),
                tick.get("ltp", 0),
                tick.get("volume", 0),
                tick.get("bid", 0),
                tick.get("ask", 0),
                tick.get("timestamp", time.time()),
                time.time(),
            ),
        )
        conn.commit()

    async def store_ticks(self, ticks: List[Dict[str, Any]]):
        """Batch store multiple ticks."""
        conn = self._get_conn()
        data = [
            (t.get("symbol"), t.get("exchange", "NSE"), t.get("ltp", 0),
             t.get("volume", 0), t.get("bid", 0), t.get("ask", 0),
             t.get("timestamp", time.time()), time.time())
            for t in ticks
        ]
        conn.executemany(
            "INSERT INTO ticks (symbol, exchange, ltp, volume, bid, ask, timestamp, received_at) VALUES (?,?,?,?,?,?,?,?)",
            data,
        )
        conn.commit()

    async def replay(self, symbol: str, from_ts: float, to_ts: float) -> List[Dict]:
        """Replay stored ticks for backtesting."""
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT symbol, ltp, volume, bid, ask, timestamp FROM ticks WHERE symbol=? AND timestamp BETWEEN ? AND ? ORDER BY timestamp",
            (symbol, from_ts, to_ts),
        ).fetchall()
        return [
            {"symbol": r[0], "ltp": r[1], "volume": r[2], "bid": r[3], "ask": r[4], "timestamp": r[5]}
            for r in rows
        ]

    async def aggregate_ohlcv(self, symbol: str, from_ts: float, to_ts: float, interval_seconds: int = 60) -> List[Dict]:
        """Aggregate raw ticks into OHLCV candles."""
        ticks = await self.replay(symbol, from_ts, to_ts)
        if not ticks:
            return []

        candles = []
        current_bucket = None
        o = h = l = c = 0.0
        vol = 0

        for tick in ticks:
            bucket = int(tick["timestamp"] // interval_seconds) * interval_seconds
            if bucket != current_bucket:
                if current_bucket is not None:
                    candles.append({
                        "timestamp": current_bucket, "open": o, "high": h,
                        "low": l, "close": c, "volume": vol,
                    })
                current_bucket = bucket
                o = h = l = c = tick["ltp"]
                vol = tick["volume"]
            else:
                h = max(h, tick["ltp"])
                l = min(l, tick["ltp"])
                c = tick["ltp"]
                vol += tick["volume"]

        if current_bucket is not None:
            candles.append({
                "timestamp": current_bucket, "open": o, "high": h,
                "low": l, "close": c, "volume": vol,
            })

        return candles

    async def cleanup(self, older_than_days: int = 7):
        """Remove old tick data."""
        conn = self._get_conn()
        cutoff = time.time() - (older_than_days * 86400)
        conn.execute("DELETE FROM ticks WHERE timestamp < ?", (cutoff,))
        conn.commit()
        logger.info(f"Tick data cleanup: removed ticks older than {older_than_days} days")

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None


def get_tick_storage() -> TickStorage:
    global _storage
    if _storage is None:
        _storage = TickStorage()
    return _storage
