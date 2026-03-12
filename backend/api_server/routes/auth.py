"""Authentication routes — Google OAuth, JWT management, user profiles."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
import time
import hmac
import hashlib
from loguru import logger

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

# Simple in-memory session store (swap with DB for production)
_sessions = {}
_JWT_SECRET = "quant-ai-lab-secret-key-change-in-production"


class GoogleAuthRequest(BaseModel):
    id_token: str


class RefreshRequest(BaseModel):
    refresh_token: str


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    user: dict


def _generate_token(user_id: str) -> str:
    """Generate a simple JWT-like token."""
    payload = f"{user_id}:{int(time.time()) + 3600}"
    signature = hmac.new(_JWT_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()[:16]
    return f"{payload}:{signature}"


def _verify_token(token: str) -> Optional[str]:
    """Verify token and return user_id."""
    try:
        parts = token.split(":")
        if len(parts) != 3:
            return None
        user_id, expiry, sig = parts
        if int(expiry) < time.time():
            return None
        expected_sig = hmac.new(_JWT_SECRET.encode(), f"{user_id}:{expiry}".encode(), hashlib.sha256).hexdigest()[:16]
        if not hmac.compare_digest(sig, expected_sig):
            return None
        return user_id
    except Exception:
        return None


@router.post("/google", response_model=AuthResponse)
async def google_auth(req: GoogleAuthRequest):
    """Exchange Google id_token for app JWT."""
    try:
        # In production, verify Google id_token with Google's public keys
        # For now, create a session based on the token
        user_id = f"usr_{uuid.uuid4().hex[:8]}"
        user = {
            "id": user_id,
            "email": "user@gmail.com",
            "name": "User",
            "picture": "",
        }

        access_token = _generate_token(user_id)
        refresh_token = f"refresh_{uuid.uuid4().hex}"

        _sessions[user_id] = {
            "user": user,
            "refresh_token": refresh_token,
            "created_at": time.time(),
        }

        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=3600,
            user=user,
        )
    except Exception as e:
        logger.error(f"Google auth failed: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")


@router.post("/refresh")
async def refresh_token(req: RefreshRequest):
    """Refresh the access token."""
    for user_id, session in _sessions.items():
        if session.get("refresh_token") == req.refresh_token:
            new_token = _generate_token(user_id)
            return {
                "access_token": new_token,
                "expires_in": 3600,
            }
    raise HTTPException(status_code=401, detail="Invalid refresh token")


@router.post("/logout")
async def logout():
    """Revoke session."""
    return {"status": "logged_out"}


@router.get("/me")
async def get_current_user():
    """Get current user profile (simplified — no auth check for dev mode)."""
    return {
        "id": "dev_user",
        "email": "dev@quantailab.com",
        "name": "Dev User",
        "picture": "",
        "mode": "development",
    }
