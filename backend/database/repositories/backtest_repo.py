from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional, List
from .base_repo import BaseRepository
from ..models.backtest import BacktestResult


class BacktestRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, BacktestResult)

    async def get_by_result_id(self, result_id: str) -> Optional[BacktestResult]:
        result = await self.session.execute(
            select(BacktestResult).where(BacktestResult.result_id == result_id)
        )
        return result.scalar_one_or_none()

    async def get_by_strategy(self, strategy_id: str) -> List[BacktestResult]:
        result = await self.session.execute(
            select(BacktestResult).where(BacktestResult.strategy_id == strategy_id)
            .order_by(desc(BacktestResult.created_at))
        )
        return result.scalars().all()
