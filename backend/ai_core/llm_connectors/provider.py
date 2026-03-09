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
    from .oauth_handler import load_tokens
    cfg = get_ai_config()
    provider = cfg.llm_provider.lower()

    # Check: has API key OR OAuth token stored
    openai_ready = cfg.openai.api_key or bool(load_tokens("openai"))
    anthropic_ready = cfg.anthropic.api_key or bool(load_tokens("anthropic"))

    if provider == "openai" and openai_ready:
        from .openai_connector import OpenAIConnector
        return OpenAIConnector()
    elif provider == "anthropic" and anthropic_ready:
        from .anthropic_connector import AnthropicConnector
        return AnthropicConnector()
    else:
        from .ollama_connector import OllamaConnector
        return OllamaConnector()


def set_provider(provider_name: str):
    global _provider
    _provider = None  # reset; will be recreated with new config
