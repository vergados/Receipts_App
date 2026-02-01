"""Rate limiting middleware and utilities."""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable

from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class RateLimitBucket:
    """Token bucket for rate limiting."""
    
    tokens: float
    last_update: float
    max_tokens: int
    refill_rate: float  # tokens per second
    
    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens. Returns True if allowed."""
        now = time.time()
        
        # Refill tokens based on time elapsed
        elapsed = now - self.last_update
        self.tokens = min(self.max_tokens, self.tokens + elapsed * self.refill_rate)
        self.last_update = now
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    @property
    def retry_after(self) -> int:
        """Seconds until a token is available."""
        if self.tokens >= 1:
            return 0
        tokens_needed = 1 - self.tokens
        return int(tokens_needed / self.refill_rate) + 1


@dataclass
class RateLimiter:
    """In-memory rate limiter using token bucket algorithm."""
    
    # Buckets keyed by (identifier, category)
    buckets: dict[tuple[str, str], RateLimitBucket] = field(default_factory=dict)
    
    def _get_bucket(self, identifier: str, category: str, limit: int) -> RateLimitBucket:
        """Get or create a rate limit bucket."""
        key = (identifier, category)
        if key not in self.buckets:
            self.buckets[key] = RateLimitBucket(
                tokens=float(limit),
                last_update=time.time(),
                max_tokens=limit,
                refill_rate=limit / 60.0,  # Refill over 1 minute
            )
        return self.buckets[key]
    
    def check(self, identifier: str, category: str, limit: int) -> tuple[bool, int, int]:
        """
        Check if request is allowed.
        
        Returns:
            (allowed, remaining, retry_after)
        """
        bucket = self._get_bucket(identifier, category, limit)
        allowed = bucket.consume()
        remaining = int(bucket.tokens)
        retry_after = bucket.retry_after if not allowed else 0
        return allowed, remaining, retry_after
    
    def cleanup_old_buckets(self, max_age_seconds: int = 3600) -> int:
        """Remove buckets that haven't been used recently."""
        now = time.time()
        old_keys = [
            key for key, bucket in self.buckets.items()
            if now - bucket.last_update > max_age_seconds
        ]
        for key in old_keys:
            del self.buckets[key]
        return len(old_keys)


# Global rate limiter instance
rate_limiter = RateLimiter()


def get_rate_limit_category(path: str, method: str) -> tuple[str, int]:
    """Determine rate limit category and limit for a request."""
    # Auth endpoints
    if path.startswith("/api/v1/auth"):
        return "auth", settings.rate_limit_auth_per_minute
    
    # Upload endpoints
    if path.startswith("/api/v1/uploads"):
        return "upload", settings.rate_limit_upload_per_minute
    
    # Export endpoints
    if path.startswith("/api/v1/exports") or path.endswith("/export"):
        return "export", settings.rate_limit_export_per_minute
    
    # Write operations
    if method in ("POST", "PUT", "PATCH", "DELETE"):
        return "write", settings.rate_limit_write_per_minute
    
    # Read operations (default)
    return "read", settings.rate_limit_read_per_minute


def get_client_identifier(request: Request) -> str:
    """Get a unique identifier for the client."""
    # Check for authenticated user
    if hasattr(request.state, "user") and request.state.user:
        return f"user:{request.state.user.id}"
    
    # Fall back to IP address
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Take the first IP in the chain
        ip = forwarded.split(",")[0].strip()
    else:
        ip = request.client.host if request.client else "unknown"
    
    return f"ip:{ip}"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware that enforces rate limits."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not settings.rate_limit_enabled:
            return await call_next(request)
        
        # Skip rate limiting for health checks
        if request.url.path == "/health":
            return await call_next(request)
        
        identifier = get_client_identifier(request)
        category, limit = get_rate_limit_category(request.url.path, request.method)
        
        allowed, remaining, retry_after = rate_limiter.check(identifier, category, limit)
        
        if not allowed:
            logger.warning(
                "Rate limit exceeded",
                identifier=identifier,
                category=category,
                path=request.url.path,
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": {
                        "code": "RATE_LIMITED",
                        "message": "Too many requests. Please try again later.",
                        "retry_after": retry_after,
                    }
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + retry_after),
                },
            )
        
        response = await call_next(request)
        
        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 60)
        
        return response
