from fastapi import APIRouter, HTTPException, BackgroundTasks

router = APIRouter(prefix="/api/v1/llm", tags=["LLM OAuth"])


@router.get("/oauth/status")
async def oauth_status():
    """Check OAuth connection status for all LLM providers."""
    from backend.ai_core.llm_connectors.oauth_handler import get_oauth_status
    return {"success": True, "status": get_oauth_status()}


@router.post("/oauth/login/{provider}")
async def oauth_login(provider: str, background_tasks: BackgroundTasks):
    """
    Start OAuth login flow for OpenAI or Anthropic.
    Opens browser, waits for callback, saves encrypted tokens.
    """
    if provider not in ("openai", "anthropic"):
        raise HTTPException(status_code=400, detail="Provider must be 'openai' or 'anthropic'")

    from backend.ai_core.llm_connectors.oauth_handler import do_oauth_login
    result = await do_oauth_login(provider)

    # Reset LLM provider so it picks up the new token
    if result.get("success"):
        from backend.ai_core.llm_connectors.provider import set_provider
        set_provider(provider)

    return result


@router.post("/oauth/logout/{provider}")
async def oauth_logout(provider: str):
    """Revoke and delete OAuth tokens for a provider."""
    if provider not in ("openai", "anthropic"):
        raise HTTPException(status_code=400, detail="Provider must be 'openai' or 'anthropic'")

    from backend.ai_core.llm_connectors.oauth_handler import do_logout
    await do_logout(provider)

    # Reset provider to fallback (Ollama)
    from backend.ai_core.llm_connectors.provider import set_provider
    set_provider("ollama")

    return {"success": True, "message": f"Logged out from {provider}"}


@router.get("/oauth/token/{provider}")
async def get_token_info(provider: str):
    """Return token metadata (no raw tokens exposed)."""
    from backend.ai_core.llm_connectors.oauth_handler import load_tokens
    tokens = load_tokens(provider)
    if not tokens:
        return {"success": True, "connected": False}
    return {
        "success": True,
        "connected": True,
        "expires_at": tokens.get("expires_at"),
        "method": "oauth",
        "provider": provider,
    }


@router.get("/providers")
async def list_providers():
    """Return all available LLM providers and their connection status."""
    from backend.config import get_ai_config
    from backend.ai_core.llm_connectors.oauth_handler import get_oauth_status, load_tokens

    cfg = get_ai_config()
    oauth = get_oauth_status()

    return {
        "success": True,
        "active_provider": cfg.llm_provider,
        "providers": {
            "openai": {
                "api_key_set": bool(cfg.openai.api_key),
                "oauth_connected": oauth.get("openai", {}).get("connected", False),
                "model": cfg.openai.model,
                "available": bool(cfg.openai.api_key) or oauth.get("openai", {}).get("connected", False),
            },
            "anthropic": {
                "api_key_set": bool(cfg.anthropic.api_key),
                "oauth_connected": oauth.get("anthropic", {}).get("connected", False),
                "model": cfg.anthropic.model,
                "available": bool(cfg.anthropic.api_key) or oauth.get("anthropic", {}).get("connected", False),
            },
            "ollama": {
                "api_key_set": None,
                "oauth_connected": None,
                "model": cfg.ollama.model,
                "base_url": cfg.ollama.base_url,
                "available": True,  # Always available locally
            },
        },
    }
