"""Pajakia — Indonesian Tax Preparation Platform."""

import logging
import time
import uuid

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import get_settings
from app.routers import auth, webhook, filings, tax, spt, consultant, portal, compliance

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
audit_logger = logging.getLogger("pajakia.audit")

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="AI-powered tax preparation for Indonesia — PPh, PPN, and more.",
    version="0.2.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url=None,
)

# --- CORS (locked down) ---
allowed_origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)


# --- Security Headers Middleware ---
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        return response


app.add_middleware(SecurityHeadersMiddleware)


# --- Rate Limiting Middleware ---
class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiter. Use Redis in production for multi-process."""

    def __init__(self, app, default_rpm: int = 100, auth_rpm: int = 10):
        super().__init__(app)
        self.default_rpm = default_rpm
        self.auth_rpm = auth_rpm
        self._buckets: dict[str, list[float]] = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path
        now = time.time()
        window = 60.0

        is_auth = "/auth/" in path
        limit = self.auth_rpm if is_auth else self.default_rpm
        key = f"{client_ip}:{'auth' if is_auth else 'default'}"

        bucket = self._buckets.setdefault(key, [])
        bucket[:] = [t for t in bucket if now - t < window]

        if len(bucket) >= limit:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please slow down."},
                headers={"Retry-After": "60"},
            )

        bucket.append(now)
        return await call_next(request)


app.add_middleware(
    RateLimitMiddleware,
    default_rpm=settings.rate_limit_per_minute,
    auth_rpm=settings.rate_limit_auth_per_minute,
)


# --- Audit Logging Middleware ---
class AuditLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
        start = time.time()

        response = await call_next(request)

        duration_ms = round((time.time() - start) * 1000, 1)
        client_ip = request.client.host if request.client else "unknown"

        method = request.method
        path = request.url.path
        if method in ("POST", "PUT", "PATCH", "DELETE") or "/consultant/" in path or "/filings/" in path:
            auth_header = request.headers.get("Authorization", "")
            user_hint = "anonymous"
            if auth_header.startswith("Bearer "):
                try:
                    from app.core.security import decode_token
                    payload = decode_token(auth_header.split(" ", 1)[1])
                    user_hint = payload.get("email", payload.get("sub", "unknown"))
                except Exception:
                    user_hint = "invalid-token"

            audit_logger.info(
                "AUDIT req_id=%s user=%s method=%s path=%s status=%s ip=%s duration=%sms",
                request_id, user_hint, method, path, response.status_code,
                client_ip, duration_ms,
            )

        response.headers["X-Request-ID"] = request_id
        return response


app.add_middleware(AuditLogMiddleware)


# --- Global Exception Handler ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Never leak internal details in production."""
    if settings.debug:
        raise exc
    audit_logger.error(
        "Unhandled error path=%s error=%s",
        request.url.path, str(exc),
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


# Routers
app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(webhook.router, prefix=settings.api_prefix)
app.include_router(filings.router, prefix=settings.api_prefix)
app.include_router(tax.router, prefix=settings.api_prefix)
app.include_router(spt.router, prefix=settings.api_prefix)
app.include_router(consultant.router, prefix=settings.api_prefix)
app.include_router(portal.router, prefix=settings.api_prefix)
app.include_router(compliance.router, prefix=settings.api_prefix)


@app.get("/")
async def root():
    return {
        "app": settings.app_name,
        "version": "0.2.0",
        "status": "running",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
