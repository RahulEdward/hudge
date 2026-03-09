import uuid
from typing import Dict, Any
from loguru import logger


REGIMES = {0: "TRENDING", 1: "MEAN_REVERTING", 2: "HIGH_VOLATILITY", 3: "LOW_VOLATILITY"}


class RegimeModel:
    """HMM + K-Means market regime classifier."""

    def __init__(self):
        self.model = None

    async def train(self, symbol: str, timeframe: str = "1D", lookback_days: int = 500) -> Dict[str, Any]:
        from backend.data_engine.historical_loader import get_historical_loader
        import numpy as np

        loader = get_historical_loader()
        df = await loader.get_dataframe(symbol, timeframe, limit=lookback_days)
        if df is None or len(df) < 50:
            return {"error": "Insufficient data"}

        returns = df["close"].pct_change().dropna()
        vol = returns.rolling(20).std().dropna()
        features = np.column_stack([returns.tail(len(vol)), vol])

        try:
            from sklearn.cluster import KMeans
            self.model = KMeans(n_clusters=4, random_state=42, n_init=10)
            self.model.fit(features)
            current_regime = int(self.model.predict(features[-1:])[0])
            logger.info(f"Regime model trained: {symbol} | Current: {REGIMES.get(current_regime)}")
            return {
                "model_id": str(uuid.uuid4())[:12],
                "symbol": symbol,
                "current_regime": REGIMES.get(current_regime, "UNKNOWN"),
            }
        except Exception as e:
            return {"error": str(e)}

    async def predict(self, symbol: str, timeframe: str = "1D") -> str:
        """Return current market regime."""
        from backend.data_engine.historical_loader import get_historical_loader
        import numpy as np

        loader = get_historical_loader()
        df = await loader.get_dataframe(symbol, timeframe, limit=60)
        if df is None or df.empty:
            return "UNKNOWN"

        returns = df["close"].pct_change().dropna()
        vol = returns.std()
        mean = abs(returns.mean())
        trend_strength = mean / (vol + 1e-10)

        if vol > 0.025:
            return "HIGH_VOLATILITY"
        elif trend_strength > 0.5:
            return "TRENDING"
        elif trend_strength < 0.1:
            return "LOW_VOLATILITY"
        return "MEAN_REVERTING"
