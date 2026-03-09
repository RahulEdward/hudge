from typing import Dict, Any, List
from backend.ai_core.agents.base_agent import BaseAgent

_agent = None


class DataAgent(BaseAgent):
    name = "data_agent"

    async def handle(self, message: str, session_id: str) -> str:
        return "Data Agent ready. I can fetch market data, historical OHLCV, and compute indicators."

    async def fetch_ohlcv(self, symbol: str, timeframe: str = "1D", limit: int = 100) -> List[Dict]:
        from backend.data_engine.historical_loader import get_historical_loader
        loader = get_historical_loader()
        return await loader.get_ohlcv(symbol, timeframe, limit)

    async def get_live_quote(self, symbol: str) -> Dict[str, Any]:
        from backend.broker_gateway.broker_manager import get_broker_manager
        bm = get_broker_manager()
        return await bm.get_quote(symbol)

    async def compute_features(self, symbol: str, timeframe: str = "1D") -> Dict[str, Any]:
        from backend.data_engine.historical_loader import get_historical_loader
        from backend.data_engine.feature_builder import build_features
        loader = get_historical_loader()
        df = await loader.get_dataframe(symbol, timeframe, limit=300)
        if df is None or df.empty:
            return {}
        features = build_features(df)
        return features.tail(1).to_dict(orient="records")[0] if not features.empty else {}


def get_data_agent() -> DataAgent:
    global _agent
    if _agent is None:
        _agent = DataAgent()
    return _agent
