from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List
from .base_repo import BaseRepository
from ..models.alert import Alert


class AlertRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Alert)

    async def get_unread(self) -> List[Alert]:
        result = await self.session.execute(
            select(Alert).where(Alert.is_read == 0).order_by(desc(Alert.created_at))
        )
        return result.scalars().all()

    async def get_recent(self, limit: int = 50) -> List[Alert]:
        result = await self.session.execute(
            select(Alert).order_by(desc(Alert.created_at)).limit(limit)
        )
        return result.scalars().all()
