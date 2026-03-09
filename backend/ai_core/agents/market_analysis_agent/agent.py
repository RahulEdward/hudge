from typing import Dict, Any
from loguru import logger
from backend.ai_core.agents.base_agent import BaseAgent

_agent = None


class MarketAnalysisAgent(BaseAgent):
    name = "market_analysis"

    async def handle(self, message: str, session_id: str) -> str:
        # Extract symbol from message
        symbol = self._extract_symbol(message)
        analysis = await self.analyze(symbol=symbol)
        return analysis.get("summary", "Market analysis complete.")

    def _extract_symbol(self, message: str) -> str:
        common = ["NIFTY", "BANKNIFTY", "FINNIFTY", "RELIANCE", "TCS", "INFY", "HDFC", "ICICI"]
        msg_upper = message.upper()
        for sym in common:
            if sym in msg_upper:
                return sym
        return "NIFTY"

    async def analyze(self, symbol: str = "NIFTY", timeframe: str = "1D") -> Dict[str, Any]:
        from backend.data_engine.historical_loader import get_historical_loader
        from backend.data_engine.feature_builder import compute_indicators

        loader = get_historical_loader()
        df = await loader.get_dataframe(symbol, timeframe, limit=200)

        if df is None or df.empty:
            return {"symbol": symbol, "error": "No data available", "summary": "Could not fetch market data"}

        # Compute indicators
        indicators = compute_indicators(df, ["ema20", "ema50", "rsi", "macd", "atr", "bb"])

        # Trend detection
        close = df["close"].iloc[-1]
        ema20_vals = indicators.get("ema_20", [])
        ema50_vals = indicators.get("ema_50", [])
        rsi_vals = indicators.get("rsi", [])

        ema20 = ema20_vals[-1] if ema20_vals else close
        ema50 = ema50_vals[-1] if ema50_vals else close
        rsi = rsi_vals[-1] if rsi_vals else 50

        trend = "BULLISH" if ema20 > ema50 else "BEARISH"
        volatility = "HIGH" if indicators.get("atr", [1])[-1] > close * 0.02 else "NORMAL"

        market_data = {
            "symbol": symbol,
            "timeframe": timeframe,
            "last_price": round(close, 2),
            "ema20": round(ema20, 2),
            "ema50": round(ema50, 2),
            "rsi": round(rsi, 2),
            "trend": trend,
            "volatility": volatility,
        }

        # LLM qualitative analysis
        llm = await self.get_llm()
        try:
            summary = await llm.analyze_market(market_data)
        except Exception as e:
            summary = f"Trend: {trend} | RSI: {rsi:.1f} | Volatility: {volatility} | LTP: {close:.2f}"

        return {**market_data, "summary": summary}

    async def detect_market_regime(self, symbol: str) -> str:
        """Trending / Mean-Reverting / Volatile / Quiet."""
        df = await self._get_data(symbol)
        if df is None:
            return "UNKNOWN"
        returns = df["close"].pct_change().dropna()
        vol = returns.std()
        if vol > 0.025:
            return "VOLATILE"
        trend_strength = abs(returns.mean()) / (vol + 1e-10)
        if trend_strength > 0.5:
            return "TRENDING"
        if trend_strength < 0.1:
            return "QUIET"
        return "MEAN_REVERTING"

    async def _get_data(self, symbol):
        from backend.data_engine.historical_loader import get_historical_loader
        return await get_historical_loader().get_dataframe(symbol, "1D", limit=60)


def get_market_analysis_agent() -> MarketAnalysisAgent:
    global _agent
    if _agent is None:
        _agent = MarketAnalysisAgent()
    return _agent
