from typing import AsyncGenerator, Optional
from loguru import logger
from .base import LLMBase


class OpenAIConnector(LLMBase):
    def __init__(self):
        from backend.config import get_ai_config
        cfg = get_ai_config().openai
        self.api_key = cfg.api_key
        self.model = cfg.model
        self.temperature = cfg.temperature
        self.max_tokens = cfg.max_tokens
        self._client = None

    def _get_client(self):
        if not self._client:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(api_key=self.api_key)
        return self._client

    async def generate_text(self, prompt: str, system: str = None, **kwargs) -> str:
        try:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            client = self._get_client()
            response = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return f"[OpenAI Error: {e}]"

    async def stream_response(self, prompt: str, system: str = None, **kwargs) -> AsyncGenerator[str, None]:
        try:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            client = self._get_client()
            stream = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                temperature=kwargs.get("temperature", self.temperature),
            )
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"[OpenAI Error: {e}]"
