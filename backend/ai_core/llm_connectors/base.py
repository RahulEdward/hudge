from abc import ABC, abstractmethod
from typing import List, Dict, Any, AsyncGenerator, Optional


class LLMBase(ABC):
    """Unified interface for all LLM providers."""

    @abstractmethod
    async def generate_text(self, prompt: str, system: str = None, **kwargs) -> str:
        """Generate text from a prompt."""

    @abstractmethod
    async def stream_response(self, prompt: str, system: str = None, **kwargs) -> AsyncGenerator[str, None]:
        """Stream response tokens."""

    async def analyze_market(self, market_data: Dict[str, Any]) -> str:
        prompt = f"""You are a quantitative trading analyst specializing in Indian markets.
Analyze the following market data and provide insights:

{market_data}

Provide: trend direction, key levels, volatility assessment, and trading opportunity score (0-10)."""
        return await self.generate_text(prompt)

    async def build_strategy(self, analysis: str, symbol: str) -> Dict[str, Any]:
        import json
        prompt = f"""You are an algorithmic trading strategy designer for Indian markets.
Based on this market analysis for {symbol}:
{analysis}

Generate a complete trading strategy in JSON format with:
- name: string
- description: string
- indicators: list of indicator names
- entry_rules: dict with conditions
- exit_rules: dict with conditions
- parameters: dict with indicator parameters
- timeframe: string
- risk_per_trade_pct: float (0.5-2.0)

Return ONLY valid JSON, no other text."""
        response = await self.generate_text(prompt)
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception:
            pass
        return {"name": f"AI Strategy {symbol}", "description": analysis[:200],
                "indicators": ["EMA", "RSI"], "entry_rules": {}, "exit_rules": {},
                "parameters": {}, "timeframe": "1D", "risk_per_trade_pct": 1.0}

    async def reason_about_trade(self, context: Dict[str, Any]) -> str:
        prompt = f"""You are a risk-conscious trading AI for Indian markets.
Evaluate this trade opportunity and provide your reasoning:
{context}

Assess: entry quality, risk/reward, market conditions alignment, confidence (0-100%)."""
        return await self.generate_text(prompt)
