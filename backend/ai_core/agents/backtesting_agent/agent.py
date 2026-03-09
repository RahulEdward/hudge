from typing import Dict, Any
from backend.ai_core.agents.base_agent import BaseAgent

_agent = None


class BacktestingAgent(BaseAgent):
    name = "backtesting"

    async def handle(self, message: str, session_id: str) -> str:
        return "Backtesting Agent ready. Provide a strategy ID or parameters to run a backtest."

    async def backtest(self, strategy_id: str, symbol: str, timeframe: str = "1D",
                       start_date: str = None, end_date: str = None,
                       initial_capital: float = 1000000) -> Dict[str, Any]:
        from backend.backtesting_engine.simulator import run_backtest
        return await run_backtest(
            strategy_id=strategy_id,
            symbol=symbol,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
        )


def get_backtesting_agent() -> BacktestingAgent:
    global _agent
    if _agent is None:
        _agent = BacktestingAgent()
    return _agent
