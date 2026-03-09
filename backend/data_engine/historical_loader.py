import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from loguru import logger

_loader: Optional["HistoricalLoader"] = None


class HistoricalLoader:
    """Loads and caches historical OHLCV data."""

    def __init__(self):
        self._cache: Dict[str, pd.DataFrame] = {}

    async def get_ohlcv(self, symbol: str, timeframe: str = "1D", limit: int = 100) -> List[Dict]:
        df = await self.get_dataframe(symbol, timeframe, limit=limit)
        if df is None or df.empty:
            return []
        return df.to_dict(orient="records")

    async def get_dataframe(self, symbol: str, timeframe: str = "1D", limit: int = 200) -> Optional[pd.DataFrame]:
        cache_key = f"{symbol}:{timeframe}"
        if cache_key in self._cache:
            df = self._cache[cache_key]
            if len(df) >= limit:
                return df.tail(limit)

        df = await self._fetch_from_broker(symbol, timeframe, limit)
        if df is not None and not df.empty:
            self._cache[cache_key] = df
        return df

    async def _fetch_from_broker(self, symbol: str, timeframe: str, limit: int) -> Optional[pd.DataFrame]:
        try:
            from backend.broker_gateway.broker_manager import get_broker_manager
            bm = get_broker_manager()
            to_date = datetime.now()
            days_map = {"1m": 7, "5m": 30, "15m": 60, "1h": 180, "1D": limit + 30}
            days = days_map.get(timeframe, limit + 30)
            from_date = to_date - timedelta(days=days)
            candles = await bm.get_active().get_historical_data(
                symbol, "NSE", timeframe,
                from_date.strftime("%Y-%m-%d %H:%M"),
                to_date.strftime("%Y-%m-%d %H:%M"),
            )
            if candles:
                df = pd.DataFrame(candles)
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                df = df.set_index("timestamp").sort_index()
                return df.tail(limit)
        except Exception as e:
            logger.warning(f"Could not fetch historical data for {symbol}: {e}")

        # Return synthetic data for paper/demo mode
        return self._generate_synthetic_data(symbol, timeframe, limit)

    def _generate_synthetic_data(self, symbol: str, timeframe: str, limit: int) -> pd.DataFrame:
        import numpy as np
        np.random.seed(hash(symbol) % 1000)
        prices = 1000.0 * np.exp(np.random.randn(limit).cumsum() * 0.01)
        dates = pd.date_range(end=datetime.now(), periods=limit, freq="D")
        df = pd.DataFrame({
            "open": prices * (1 + np.random.randn(limit) * 0.002),
            "high": prices * (1 + abs(np.random.randn(limit)) * 0.005),
            "low": prices * (1 - abs(np.random.randn(limit)) * 0.005),
            "close": prices,
            "volume": np.random.randint(100000, 5000000, limit),
        }, index=dates)
        df.index.name = "timestamp"
        return df


def get_historical_loader() -> HistoricalLoader:
    global _loader
    if _loader is None:
        _loader = HistoricalLoader()
    return _loader
