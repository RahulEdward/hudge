from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from .base_repo import BaseRepository
from ..models.portfolio import Portfolio


class PortfolioRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Portfolio)

    async def get_by_symbol(self, symbol: str) -> Optional[Portfolio]:
        result = await self.session.execute(select(Portfolio).where(Portfolio.symbol == symbol))
        return result.scalar_one_or_none()

    async def get_all_positions(self) -> List[Portfolio]:
        result = await self.session.execute(select(Portfolio).where(Portfolio.quantity > 0))
        return result.scalars().all()
