from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse

limiter = Limiter(key_func=get_remote_address)

def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Simple handler for rate limit errors"""
    return JSONResponse(
        status_code=429,
        content={"error": "Too many requests. Please try again later."}
    )