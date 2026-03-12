"""Authentication middleware — JWT verification for protected routes."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

# Routes that don't require authentication
PUBLIC_ROUTES = {
    "/health",
    "/api/v1/health",
    "/api/v1/auth/google",
    "/api/v1/auth/refresh",
    "/docs",
    "/openapi.json",
    "/redoc",
}

PUBLIC_PREFIXES = (
    "/ws/",
    "/api/v1/auth/",
)


class AuthMiddleware(BaseHTTPMiddleware):
    """JWT authentication middleware (permissive in dev mode)."""

    def __init__(self, app, enforce: bool = False):
        super().__init__(app)
        self.enforce = enforce

    async def dispatch(self, request, call_next):
        path = request.url.path

        # Skip auth for public routes
        if path in PUBLIC_ROUTES or any(path.startswith(p) for p in PUBLIC_PREFIXES):
            return await call_next(request)

        # In non-enforce (dev) mode, allow all requests
        if not self.enforce:
            return await call_next(request)

        # Check Authorization header
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={
                    "error": True,
                    "code": "AUTH_REQUIRED",
                    "message": "Authentication required. Provide a Bearer token.",
                },
            )

        token = auth_header[7:]
        from backend.api_server.routes.auth import _verify_token
        user_id = _verify_token(token)
        if not user_id:
            return JSONResponse(
                status_code=401,
                content={
                    "error": True,
                    "code": "AUTH_INVALID",
                    "message": "Invalid or expired authentication token.",
                },
            )

        # Attach user to request state
        request.state.user_id = user_id
        return await call_next(request)
