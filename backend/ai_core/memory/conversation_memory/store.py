"""Chat history management with context windowing and summary generation."""

from typing import Dict, List, Optional
from loguru import logger

_memory = None


class ConversationMemory:
    """Manages per-session chat history with context window management."""

    def __init__(self, max_context_messages: int = 20):
        self.max_context = max_context_messages

    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        channel: str = "desktop",
        agent_id: Optional[str] = None,
    ):
        """Save a message to conversation history."""
        try:
            from backend.database.connection import get_session
            from backend.database.repositories import ConversationRepository
            async for session in get_session():
                repo = ConversationRepository(session)
                await repo.add_message(session_id, role, content, channel, agent_id)
        except Exception as e:
            logger.error(f"Failed to save message: {e}")

    async def get_context(self, session_id: str, limit: Optional[int] = None) -> List[Dict]:
        """Retrieve recent conversation context."""
        limit = limit or self.max_context
        try:
            from backend.database.connection import get_session
            from backend.database.repositories import ConversationRepository
            async for session in get_session():
                repo = ConversationRepository(session)
                messages = await repo.get_session_history(session_id, limit=limit)
                return [{"role": m.role, "content": m.content} for m in messages]
        except Exception as e:
            logger.error(f"Failed to get context: {e}")
            return []

    async def get_summary(self, session_id: str) -> str:
        """Generate a summary of the conversation for long context compression."""
        messages = await self.get_context(session_id, limit=50)
        if len(messages) < 10:
            return ""

        try:
            from backend.ai_core.llm_connectors.provider import get_llm
            llm = get_llm()
            conversation_text = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in messages)
            prompt = (
                "Summarize this conversation in 2-3 sentences, focusing on key decisions, "
                f"strategies discussed, and action items:\n\n{conversation_text}"
            )
            return await llm.generate_text(prompt)
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return ""

    async def clear_session(self, session_id: str):
        """Clear conversation history for a session."""
        try:
            from backend.database.connection import get_session
            from backend.database.repositories import ConversationRepository
            async for session in get_session():
                repo = ConversationRepository(session)
                await repo.clear_session(session_id)
        except Exception as e:
            logger.error(f"Failed to clear session: {e}")


def get_conversation_memory() -> ConversationMemory:
    global _memory
    if _memory is None:
        _memory = ConversationMemory()
    return _memory
