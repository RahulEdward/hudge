from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseAgent(ABC):
    name: str = "base"

    @abstractmethod
    async def handle(self, message: str, session_id: str) -> str:
        """Handle a user message and return a response."""

    async def get_llm(self):
        from backend.ai_core.llm_connectors.provider import get_llm
        return get_llm()
