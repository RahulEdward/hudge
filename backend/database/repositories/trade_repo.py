from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional, List
from .base_repo import BaseRepository
from ..models.trade import Trade, Order


class OrderRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Order)

    async def get_by_order_id(self, order_id: str) -> Optional[Order]:
        result = await self.session.execute(select(Order).where(Order.order_id == order_id))
        return result.scalar_one_or_none()

    async def get_open_orders(self) -> List[Order]:
        result = await self.session.execute(
            select(Order).where(Order.status.in_(["pending", "placed", "open", "partial"]))
        )
        return result.scalars().all()

    async def get_by_symbol(self, symbol: str, limit: int = 50) -> List[Order]:
        result = await self.session.execute(
            select(Order).where(Order.symbol == symbol).order_by(desc(Order.created_at)).limit(limit)
        )
        return result.scalars().all()


class TradeRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Trade)

    async def get_by_trade_id(self, trade_id: str) -> Optional[Trade]:
        result = await self.session.execute(select(Trade).where(Trade.trade_id == trade_id))
        return result.scalar_one_or_none()

    async def get_recent(self, limit: int = 50) -> List[Trade]:
        result = await self.session.execute(
            select(Trade).order_by(desc(Trade.executed_at)).limit(limit)
        )
        return result.scalars().all()

    async def get_by_strategy(self, strategy_id: str) -> List[Trade]:
        result = await self.session.execute(
            select(Trade).where(Trade.strategy_id == strategy_id).order_by(desc(Trade.executed_at))
        )
        return result.scalars().all()
