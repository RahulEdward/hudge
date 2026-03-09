from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List
from .base_repo import BaseRepository
from ..models.conversation import Conversation


class ConversationRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Conversation)

    async def get_session_history(self, session_id: str, limit: int = 50) -> List[Conversation]:
        result = await self.session.execute(
            select(Conversation)
            .where(Conversation.session_id == session_id)
            .order_by(Conversation.created_at)
            .limit(limit)
        )
        return result.scalars().all()

    async def add_message(self, session_id: str, role: str, content: str, channel: str = "desktop", agent_id: str = None) -> Conversation:
        msg = Conversation(
            session_id=session_id,
            role=role,
            content=content,
            channel=channel,
            agent_id=agent_id
        )
        return await self.create(msg)
