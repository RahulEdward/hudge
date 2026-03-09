from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional, List
from .base_repo import BaseRepository
from ..models.strategy import Strategy


class StrategyRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Strategy)

    async def get_by_strategy_id(self, strategy_id: str) -> Optional[Strategy]:
        result = await self.session.execute(select(Strategy).where(Strategy.strategy_id == strategy_id))
        return result.scalar_one_or_none()

    async def get_by_status(self, status: str) -> List[Strategy]:
        result = await self.session.execute(
            select(Strategy).where(Strategy.status == status).order_by(desc(Strategy.created_at))
        )
        return result.scalars().all()

    async def get_pending_approval(self) -> List[Strategy]:
        result = await self.session.execute(
            select(Strategy).where(Strategy.status == "pending_approval")
        )
        return result.scalars().all()

    async def get_active(self) -> List[Strategy]:
        result = await self.session.execute(
            select(Strategy).where(Strategy.status.in_(["approved", "live", "monitoring"]))
        )
        return result.scalars().all()
