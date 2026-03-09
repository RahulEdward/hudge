"""
OAuth 2.0 + PKCE handler for OpenAI and Anthropic LLM providers.

Flow:
  User clicks Login → Authorization URL opens in browser
  → User authorizes → Callback on localhost:5790
  → Exchange auth code for tokens
  → Encrypt & store tokens
  → Auto-refresh before expiry
"""

import os
import json
import base64
import hashlib
import secrets
import asyncio
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path
from urllib.parse import urlencode, parse_qs, urlparse
from cryptography.fernet import Fernet
from loguru import logger

# ─── Token Storage ────────────────────────────────────────────────────────────

TOKEN_FILE = Path("configs/.llm_tokens.enc")
_fernet: Optional[Fernet] = None


def _get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        key_file = Path("configs/.token_key")
        if key_file.exists():
            key = key_file.read_bytes()
        else:
            key = Fernet.generate_key()
            key_file.parent.mkdir(parents=True, exist_ok=True)
            key_file.write_bytes(key)
        _fernet = Fernet(key)
    return _fernet


def save_tokens(provider: str, tokens: Dict[str, Any]):
    """Encrypt and save tokens to disk."""
    existing = load_all_tokens()
    existing[provider] = {**tokens, "saved_at": datetime.utcnow().isoformat()}
    encrypted = _get_fernet().encrypt(json.dumps(existing).encode())
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_bytes(encrypted)
    logger.info(f"Tokens saved for provider: {provider}")


def load_all_tokens() -> Dict[str, Any]:
    if not TOKEN_FILE.exists():
        return {}
    try:
        data = _get_fernet().decrypt(TOKEN_FILE.read_bytes())
        return json.loads(data)
    except Exception as e:
        logger.warning(f"Could not load tokens: {e}")
        return {}


def load_tokens(provider: str) -> Optional[Dict[str, Any]]:
    return load_all_tokens().get(provider)


def delete_tokens(provider: str):
    existing = load_all_tokens()
    existing.pop(provider, None)
    if existing:
        encrypted = _get_fernet().encrypt(json.dumps(existing).encode())
        TOKEN_FILE.write_bytes(encrypted)
    elif TOKEN_FILE.exists():
        TOKEN_FILE.unlink()
    logger.info(f"Tokens deleted for provider: {provider}")


# ─── PKCE Helpers ─────────────────────────────────────────────────────────────

def _generate_code_verifier() -> str:
    return base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b"=").decode()


def _generate_code_challenge(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode()).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode()


# ─── OAuth Configs ────────────────────────────────────────────────────────────

OAUTH_CONFIGS = {
    "openai": {
        "auth_url": "https://auth.openai.com/authorize",
        "token_url": "https://auth.openai.com/oauth/token",
        "client_id": "app-quant-ai-lab",  # Replace with your registered client_id
        "scopes": ["openai.model.request", "openai.organization.read"],
        "redirect_uri": "http://localhost:5790/callback/openai",
    },
    "anthropic": {
        "auth_url": "https://claude.ai/oauth/authorize",
        "token_url": "https://claude.ai/oauth/token",
        "client_id": "app-quant-ai-lab",  # Replace with your registered client_id
        "scopes": ["claude.messages", "claude.models"],
        "redirect_uri": "http://localhost:5790/callback/anthropic",
    },
}

CALLBACK_PORT = 5790


# ─── OAuth Handler ─────────────────────────────────────────────────────────────

class OAuthHandler:
    """
    Manages OAuth 2.0 + PKCE authentication for OpenAI and Anthropic.
    Starts a local HTTP server to catch the authorization callback.
    """

    def __init__(self, provider: str):
        if provider not in OAUTH_CONFIGS:
            raise ValueError(f"Unknown provider: {provider}")
        self.provider = provider
        self.cfg = OAUTH_CONFIGS[provider]
        self._code_verifier = _generate_code_verifier()
        self._state = secrets.token_urlsafe(16)
        self._received_code: Optional[str] = None
        self._error: Optional[str] = None
        self._server = None

    def get_auth_url(self) -> str:
        """Generate the authorization URL to open in the browser."""
        params = {
            "response_type": "code",
            "client_id": self.cfg["client_id"],
            "redirect_uri": self.cfg["redirect_uri"],
            "scope": " ".join(self.cfg["scopes"]),
            "state": self._state,
            "code_challenge": _generate_code_challenge(self._code_verifier),
            "code_challenge_method": "S256",
        }
        return f"{self.cfg['auth_url']}?{urlencode(params)}"

    async def wait_for_callback(self, timeout: int = 120) -> Optional[str]:
        """
        Start local HTTP server, wait for the OAuth callback, return the auth code.
        """
        loop = asyncio.get_event_loop()
        code_future = loop.create_future()

        def _handle_request(conn, addr):
            try:
                data = conn.recv(4096).decode()
                first_line = data.split("\r\n")[0]  # GET /callback?code=... HTTP/1.1
                path = first_line.split(" ")[1]
                params = parse_qs(urlparse(path).query)

                if "error" in params:
                    error = params["error"][0]
                    response = b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n"
                    response += f"<h2>Error: {error}</h2><p>You can close this tab.</p>".encode()
                    conn.send(response)
                    loop.call_soon_threadsafe(
                        code_future.set_exception, Exception(f"OAuth error: {error}")
                    )
                elif "code" in params:
                    code = params["code"][0]
                    state = params.get("state", [""])[0]
                    if state != self._state:
                        conn.send(b"HTTP/1.1 400 Bad Request\r\n\r\nState mismatch")
                        loop.call_soon_threadsafe(
                            code_future.set_exception, Exception("State mismatch — possible CSRF")
                        )
                    else:
                        response = b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n"
                        response += b"<h2>Authorization successful!</h2><p>You can close this tab and return to Quant AI Lab.</p>"
                        conn.send(response)
                        loop.call_soon_threadsafe(code_future.set_result, code)
                conn.close()
            except Exception as e:
                logger.error(f"Callback handler error: {e}")

        import socket
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind(("localhost", CALLBACK_PORT))
        server_sock.listen(1)
        server_sock.settimeout(timeout)

        def _accept_loop():
            try:
                conn, addr = server_sock.accept()
                _handle_request(conn, addr)
            except socket.timeout:
                loop.call_soon_threadsafe(
                    code_future.set_exception, TimeoutError("OAuth callback timed out")
                )
            finally:
                server_sock.close()

        thread = threading.Thread(target=_accept_loop, daemon=True)
        thread.start()

        logger.info(f"Waiting for OAuth callback on port {CALLBACK_PORT}...")
        return await asyncio.wait_for(code_future, timeout=timeout)

    async def exchange_code(self, auth_code: str) -> Dict[str, Any]:
        """Exchange authorization code for access + refresh tokens."""
        import httpx
        payload = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": self.cfg["redirect_uri"],
            "client_id": self.cfg["client_id"],
            "code_verifier": self._code_verifier,
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(self.cfg["token_url"], data=payload)
            response.raise_for_status()
            return response.json()

    async def refresh_tokens(self, refresh_token: str) -> Dict[str, Any]:
        """Get new access token using refresh token."""
        import httpx
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.cfg["client_id"],
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(self.cfg["token_url"], data=payload)
            response.raise_for_status()
            return response.json()


# ─── Full Login Flow ──────────────────────────────────────────────────────────

async def do_oauth_login(provider: str) -> Dict[str, Any]:
    """
    Complete OAuth login flow:
    1. Generate auth URL
    2. Open browser
    3. Wait for callback
    4. Exchange code for tokens
    5. Save encrypted tokens
    """
    handler = OAuthHandler(provider)
    auth_url = handler.get_auth_url()

    logger.info(f"Opening browser for {provider} OAuth login...")
    import webbrowser
    webbrowser.open(auth_url)

    try:
        auth_code = await handler.wait_for_callback(timeout=120)
        tokens = await handler.exchange_code(auth_code)

        # Add expiry time
        expires_in = tokens.get("expires_in", 3600)
        tokens["expires_at"] = (datetime.utcnow() + timedelta(seconds=expires_in)).isoformat()
        tokens["provider"] = provider

        save_tokens(provider, tokens)
        logger.info(f"OAuth login successful for {provider}")
        return {"success": True, "provider": provider, "expires_at": tokens["expires_at"]}

    except Exception as e:
        logger.error(f"OAuth login failed for {provider}: {e}")
        return {"success": False, "error": str(e)}


async def get_valid_token(provider: str) -> Optional[str]:
    """Get a valid access token, refreshing if needed."""
    tokens = load_tokens(provider)
    if not tokens:
        return None

    access_token = tokens.get("access_token")
    expires_at_str = tokens.get("expires_at")
    refresh_token = tokens.get("refresh_token")

    # Check expiry (refresh 5 min before)
    if expires_at_str:
        expires_at = datetime.fromisoformat(expires_at_str)
        if datetime.utcnow() >= expires_at - timedelta(minutes=5):
            if refresh_token:
                try:
                    handler = OAuthHandler(provider)
                    new_tokens = await handler.refresh_tokens(refresh_token)
                    expires_in = new_tokens.get("expires_in", 3600)
                    new_tokens["expires_at"] = (datetime.utcnow() + timedelta(seconds=expires_in)).isoformat()
                    new_tokens["provider"] = provider
                    new_tokens.setdefault("refresh_token", refresh_token)
                    save_tokens(provider, new_tokens)
                    logger.info(f"Token refreshed for {provider}")
                    return new_tokens.get("access_token")
                except Exception as e:
                    logger.error(f"Token refresh failed for {provider}: {e}")
                    return None
            return None

    return access_token


async def do_logout(provider: str):
    """Revoke and delete stored tokens."""
    tokens = load_tokens(provider)
    if tokens and tokens.get("access_token"):
        try:
            import httpx
            revoke_url = {
                "openai": "https://auth.openai.com/oauth/revoke",
                "anthropic": "https://claude.ai/oauth/revoke",
            }.get(provider)
            if revoke_url:
                async with httpx.AsyncClient(timeout=10) as client:
                    await client.post(revoke_url, data={
                        "token": tokens["access_token"],
                        "client_id": OAUTH_CONFIGS[provider]["client_id"],
                    })
        except Exception:
            pass
    delete_tokens(provider)
    logger.info(f"Logged out from {provider}")


def get_oauth_status() -> Dict[str, Any]:
    """Return OAuth connection status for all providers."""
    all_tokens = load_all_tokens()
    status = {}
    for provider in ["openai", "anthropic"]:
        tokens = all_tokens.get(provider)
        if tokens:
            expires_at = tokens.get("expires_at", "")
            try:
                expired = datetime.utcnow() >= datetime.fromisoformat(expires_at) if expires_at else True
            except Exception:
                expired = True
            status[provider] = {
                "connected": not expired,
                "expires_at": expires_at,
                "method": "oauth",
            }
        else:
            status[provider] = {"connected": False, "method": None}
    return status
