import asyncio
from typing import Set, Dict, Any, Callable, List
from loguru import logger


class MarketStream:
    """Real-time market data streaming from broker WebSocket feeds."""

    def __init__(self):
        self._subscriptions: Set[str] = set()
        self._callbacks: List[Callable] = []
        self._running = False

    def subscribe(self, symbol: str):
        self._subscriptions.add(symbol)

    def unsubscribe(self, symbol: str):
        self._subscriptions.discard(symbol)

    def on_tick(self, callback: Callable):
        self._callbacks.append(callback)

    async def start(self):
        self._running = True
        logger.info("MarketStream started")
        asyncio.create_task(self._simulation_loop())

    async def stop(self):
        self._running = False

    async def _simulation_loop(self):
        """Simulate market ticks in paper trading mode."""
        import random
        prices: Dict[str, float] = {}
        while self._running:
            for symbol in list(self._subscriptions):
                if symbol not in prices:
                    prices[symbol] = 1000.0
                # Random walk
                prices[symbol] *= (1 + random.gauss(0, 0.0003))
                tick = {
                    "symbol": symbol,
                    "ltp": round(prices[symbol], 2),
                    "volume": random.randint(1000, 50000),
                    "timestamp": asyncio.get_event_loop().time(),
                }
                # Update cache
                from backend.data_engine.data_cache import get_cache
                cache = get_cache()
                cache.update_quote_from_tick(symbol, tick)

                # Broadcast via WebSocket
                try:
                    from backend.api_server.websocket_server import get_ws_manager
                    ws_mgr = get_ws_manager()
                    await ws_mgr.broadcast({"type": "tick", "data": tick}, "market")
                except Exception:
                    pass

                for cb in self._callbacks:
                    try:
                        await cb(tick)
                    except Exception:
                        pass

            await asyncio.sleep(1)


_stream: MarketStream = None


def get_market_stream() -> MarketStream:
    global _stream
    if _stream is None:
        _stream = MarketStream()
    return _stream
