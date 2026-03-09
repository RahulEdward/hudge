from typing import AsyncGenerator
from loguru import logger
from .base import LLMBase

TRADING_SYSTEM_PROMPT = """You are an expert quantitative trading AI specializing in Indian financial markets
(NSE, BSE). You have deep knowledge of technical analysis, risk management, and algorithmic trading strategies.
Always prioritize capital preservation and provide actionable, data-driven insights."""


class AnthropicConnector(LLMBase):
    def __init__(self):
        from backend.config import get_ai_config
        cfg = get_ai_config().anthropic
        self.api_key = cfg.api_key
        self.model = cfg.model
        self.temperature = cfg.temperature
        self.max_tokens = cfg.max_tokens
        self._client = None

    def _get_client(self):
        if not self._client:
            import anthropic
            self._client = anthropic.AsyncAnthropic(api_key=self.api_key)
        return self._client

    async def generate_text(self, prompt: str, system: str = None, **kwargs) -> str:
        try:
            client = self._get_client()
            response = await client.messages.create(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                system=system or TRADING_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get("temperature", self.temperature),
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic error: {e}")
            return f"[Anthropic Error: {e}]"

    async def stream_response(self, prompt: str, system: str = None, **kwargs) -> AsyncGenerator[str, None]:
        try:
            client = self._get_client()
            async with client.messages.stream(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                system=system or TRADING_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        except Exception as e:
            yield f"[Anthropic Error: {e}]"
