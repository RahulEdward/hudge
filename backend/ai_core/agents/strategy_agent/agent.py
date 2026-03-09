import uuid
from typing import Dict, Any
from loguru import logger
from backend.ai_core.agents.base_agent import BaseAgent

_agent = None


class StrategyDiscoveryAgent(BaseAgent):
    name = "strategy_discovery"

    async def handle(self, message: str, session_id: str) -> str:
        symbol = self._extract_symbol(message)
        result = await self.discover(symbol=symbol)
        return f"Strategy discovered: **{result.get('name', 'New Strategy')}**\n{result.get('description', '')}"

    def _extract_symbol(self, message: str) -> str:
        for sym in ["NIFTY", "BANKNIFTY", "FINNIFTY", "RELIANCE", "TCS", "INFY"]:
            if sym in message.upper():
                return sym
        return "NIFTY"

    async def discover(self, symbol: str = "NIFTY", timeframe: str = "1D") -> Dict[str, Any]:
        # First get market analysis
        from backend.ai_core.agents.market_analysis_agent.agent import get_market_analysis_agent
        analysis_agent = get_market_analysis_agent()
        analysis = await analysis_agent.analyze(symbol, timeframe)

        # Use LLM to build a strategy
        llm = await self.get_llm()
        strategy_dict = await llm.build_strategy(analysis.get("summary", ""), symbol)

        # Persist strategy
        strategy_id = str(uuid.uuid4())[:12]
        strategy_dict["strategy_id"] = strategy_id
        strategy_dict["symbol"] = symbol
        strategy_dict["timeframe"] = timeframe
        strategy_dict["status"] = "discovered"

        await self._save_strategy(strategy_dict)
        logger.info(f"Strategy discovered: {strategy_dict.get('name')} ({strategy_id})")
        return strategy_dict

    async def _save_strategy(self, strategy: Dict):
        try:
            from backend.database.connection import get_session
            from backend.database.models.strategy import Strategy
            async for session in get_session():
                db_s = Strategy(
                    strategy_id=strategy["strategy_id"],
                    name=strategy.get("name", "AI Strategy"),
                    description=strategy.get("description", ""),
                    symbol=strategy.get("symbol"),
                    timeframe=strategy.get("timeframe"),
                    entry_rules=strategy.get("entry_rules", {}),
                    exit_rules=strategy.get("exit_rules", {}),
                    parameters=strategy.get("parameters", {}),
                    indicators=strategy.get("indicators", []),
                    status="discovered",
                )
                session.add(db_s)
                await session.commit()
        except Exception as e:
            logger.error(f"Failed to save strategy: {e}")


def get_strategy_agent() -> StrategyDiscoveryAgent:
    global _agent
    if _agent is None:
        _agent = StrategyDiscoveryAgent()
    return _agent
