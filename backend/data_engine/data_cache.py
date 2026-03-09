import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger

_cache: Optional["DataCache"] = None


class DataCache:
    """In-memory LRU cache for quotes and OHLCV data. Falls back to Redis if enabled."""

    def __init__(self):
        self._quotes: Dict[str, Dict] = {}
        self._ohlcv: Dict[str, Any] = {}
        self._redis = None
        self._redis_enabled = False

    async def init_redis(self):
        from backend.config import get_system_config
        cfg = get_system_config().redis
        if cfg.enabled:
            try:
                import redis.asyncio as aioredis
                self._redis = aioredis.Redis(host=cfg.host, port=cfg.port, db=cfg.db)
                await self._redis.ping()
                self._redis_enabled = True
                logger.info("Redis cache connected")
            except Exception as e:
                logger.warning(f"Redis not available, using in-memory cache: {e}")

    async def set_quote(self, symbol: str, quote: Dict[str, Any]):
        quote["_updated"] = datetime.utcnow().isoformat()
        self._quotes[symbol] = quote
        if self._redis_enabled:
            import json
            await self._redis.set(f"quote:{symbol}", json.dumps(quote), ex=5)

    async def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        if self._redis_enabled:
            import json
            raw = await self._redis.get(f"quote:{symbol}")
            if raw:
                return json.loads(raw)
        return self._quotes.get(symbol)

    async def set_ohlcv(self, key: str, data: Any, ttl: int = 300):
        self._ohlcv[key] = {"data": data, "ts": datetime.utcnow()}
        if self._redis_enabled:
            import json
            await self._redis.set(f"ohlcv:{key}", json.dumps(data, default=str), ex=ttl)

    async def get_ohlcv(self, key: str) -> Optional[Any]:
        if self._redis_enabled:
            import json
            raw = await self._redis.get(f"ohlcv:{key}")
            if raw:
                return json.loads(raw)
        entry = self._ohlcv.get(key)
        if entry:
            return entry["data"]
        return None

    def update_quote_from_tick(self, symbol: str, tick: Dict):
        existing = self._quotes.get(symbol, {})
        existing.update(tick)
        self._quotes[symbol] = existing


def get_cache() -> DataCache:
    global _cache
    if _cache is None:
        _cache = DataCache()
    return _cache
