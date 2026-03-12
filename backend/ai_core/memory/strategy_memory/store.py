"""SQLite-backed strategy memory for persistence and evolution tracking."""

from typing import Dict, Any, List, Optional
from loguru import logger

_memory = None


class StrategyMemory:
    """Persists discovered strategies and tracks performance over time."""

    async def save_strategy(self, strategy: Dict[str, Any]) -> str:
        try:
            from backend.database.connection import get_session
            from backend.database.repositories import StrategyRepository
            async for session in get_session():
                repo = StrategyRepository(session)
                record = await repo.create(strategy)
                return record.strategy_id
        except Exception as e:
            logger.error(f"Failed to save strategy: {e}")
            return ""

    async def get_strategy(self, strategy_id: str) -> Optional[Dict]:
        try:
            from backend.database.connection import get_session
            from backend.database.repositories import StrategyRepository
            async for session in get_session():
                repo = StrategyRepository(session)
                record = await repo.get_by_id(strategy_id)
                if record:
                    return {
                        "strategy_id": record.strategy_id,
                        "name": record.name,
                        "description": record.description,
                        "symbol": record.symbol,
                        "entry_rules": record.entry_rules,
                        "exit_rules": record.exit_rules,
                        "parameters": record.parameters,
                        "status": record.status,
                    }
        except Exception as e:
            logger.error(f"Failed to get strategy: {e}")
        return None

    async def list_strategies(self, status: Optional[str] = None) -> List[Dict]:
        try:
            from backend.database.connection import get_session
            from backend.database.repositories import StrategyRepository
            async for session in get_session():
                repo = StrategyRepository(session)
                records = await repo.list_all(status=status)
                return [
                    {"strategy_id": r.strategy_id, "name": r.name, "status": r.status, "symbol": r.symbol}
                    for r in records
                ]
        except Exception as e:
            logger.error(f"Failed to list strategies: {e}")
            return []

    async def update_status(self, strategy_id: str, status: str) -> bool:
        try:
            from backend.database.connection import get_session
            from backend.database.repositories import StrategyRepository
            async for session in get_session():
                repo = StrategyRepository(session)
                return await repo.update_status(strategy_id, status)
        except Exception as e:
            logger.error(f"Failed to update strategy status: {e}")
            return False

    async def get_performance_history(self, strategy_id: str) -> List[Dict]:
        try:
            from backend.database.connection import get_session
            from backend.database.repositories import BacktestRepository
            async for session in get_session():
                repo = BacktestRepository(session)
                results = await repo.get_by_strategy(strategy_id)
                return [
                    {
                        "backtest_id": r.backtest_id,
                        "win_rate": r.win_rate,
                        "sharpe_ratio": r.sharpe_ratio,
                        "max_drawdown": r.max_drawdown,
                        "net_profit": r.net_profit,
                        "created_at": str(r.created_at) if r.created_at else None,
                    }
                    for r in results
                ]
        except Exception as e:
            logger.error(f"Failed to get performance history: {e}")
            return []


def get_strategy_memory() -> StrategyMemory:
    global _memory
    if _memory is None:
        _memory = StrategyMemory()
    return _memory
