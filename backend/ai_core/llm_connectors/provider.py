from typing import Optional
from .base import LLMBase

_provider: Optional[LLMBase] = None


def get_llm() -> LLMBase:
    global _provider
    if _provider is None:
        _provider = _create_provider()
    return _provider


def _create_provider() -> LLMBase:
    from backend.config import get_ai_config
    cfg = get_ai_config()
    provider = cfg.llm_provider.lower()

    if provider == "openai" and cfg.openai.api_key:
        from .openai_connector import OpenAIConnector
        return OpenAIConnector()
    elif provider == "anthropic" and cfg.anthropic.api_key:
        from .anthropic_connector import AnthropicConnector
        return AnthropicConnector()
    else:
        from .ollama_connector import OllamaConnector
        return OllamaConnector()


def set_provider(provider_name: str):
    global _provider
    _provider = None  # reset; will be recreated with new config
