from typing import AsyncGenerator, Optional
from loguru import logger
from .base import LLMBase


class OpenAIConnector(LLMBase):
    """OpenAI connector — supports both API Key and OAuth 2.0 authentication."""

    def __init__(self):
        from backend.config import get_ai_config
        cfg = get_ai_config().openai
        self.api_key = cfg.api_key      # Used if no OAuth token
        self.model = cfg.model
        self.temperature = cfg.temperature
        self.max_tokens = cfg.max_tokens
        self._client = None

    async def _get_token(self) -> str:
        """Get auth token: OAuth token preferred, falls back to API key."""
        from .oauth_handler import get_valid_token
        oauth_token = await get_valid_token("openai")
        if oauth_token:
            logger.debug("OpenAI: using OAuth token")
            return oauth_token
        if self.api_key:
            logger.debug("OpenAI: using API key")
            return self.api_key
        raise ValueError("No OpenAI authentication available. Set api_key or login via OAuth.")

    def _get_client(self, token: str = None):
        from openai import AsyncOpenAI
        # Create fresh client with current token (OAuth tokens change on refresh)
        return AsyncOpenAI(api_key=token or self.api_key)

    async def generate_text(self, prompt: str, system: str = None, **kwargs) -> str:
        try:
            token = await self._get_token()
            client = self._get_client(token)
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
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
            token = await self._get_token()
            client = self._get_client(token)
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
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
