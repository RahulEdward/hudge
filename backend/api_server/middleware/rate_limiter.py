"""Rate limiting middleware — per-IP request throttling."""

import time
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from loguru import logger


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Simple in-memory per-IP rate limiter."""

    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict = defaultdict(list)

    async def dispatch(self, request, call_next):
        client_ip = request.client.host if request.client else "unknown"

        # Skip rate limiting for health checks and WebSocket
        if request.url.path in ("/health", "/api/v1/health") or request.url.path.startswith("/ws"):
            return await call_next(request)

        now = time.time()
        window_start = now - self.window_seconds

        # Clean old entries
        self._requests[client_ip] = [
            t for t in self._requests[client_ip] if t > window_start
        ]

        if len(self._requests[client_ip]) >= self.max_requests:
            logger.warning(f"Rate limit exceeded: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": True,
                    "code": "RATE_LIMITED",
                    "message": "Too many requests. Please slow down.",
                },
            )

        self._requests[client_ip].append(now)
        return await call_next(request)
