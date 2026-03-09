from typing import AsyncGenerator
from loguru import logger
from .base import LLMBase


class OllamaConnector(LLMBase):
    def __init__(self):
        from backend.config import get_ai_config
        cfg = get_ai_config().ollama
        self.base_url = cfg.base_url
        self.model = cfg.model
        self.temperature = cfg.temperature

    async def generate_text(self, prompt: str, system: str = None, **kwargs) -> str:
        try:
            import httpx
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": False,
                        "options": {"temperature": self.temperature},
                    },
                )
                data = response.json()
                return data["message"]["content"]
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return f"[Ollama Error: {e}] — Make sure Ollama is running: ollama serve"

    async def stream_response(self, prompt: str, system: str = None, **kwargs) -> AsyncGenerator[str, None]:
        try:
            import httpx
            import json as json_lib
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            async with httpx.AsyncClient(timeout=120) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/chat",
                    json={"model": self.model, "messages": messages, "stream": True},
                ) as response:
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                data = json_lib.loads(line)
                                content = data.get("message", {}).get("content", "")
                                if content:
                                    yield content
                            except Exception:
                                pass
        except Exception as e:
            yield f"[Ollama Error: {e}]"
