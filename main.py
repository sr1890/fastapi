from fastapi import FastAPI, Depends, Request
import uvicorn
from models import TextRequest
from utils import encodeRot13
from oauth2 import get_current_user
from auth_endpoints import router as auth_router
from rate_limiter import limiter, rate_limit_handler
from slowapi.errors import RateLimitExceeded

app = FastAPI()

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
app.include_router(auth_router)

@app.get("/")
@limiter.limit("10/minute")
def get_api_info(request: Request):
    """Show basic API information"""
    return {
        "service": "ROT13 API",
        "auth": "JWT Token required",
        "login": "POST /login with username/password",
        "users": {"testuser": "xxxxxxx", "admin": "xxxxxxx"}
    }

@app.get("/health")
@limiter.limit("30/minute")
def health_check(request: Request):
    """Simple health check"""
    return {"status": "ok"}

@app.post("/api/rot13")
@limiter.limit("20/minute")
def encode_text(request: Request, data: TextRequest, user = Depends(get_current_user)):
    """Encode text using ROT13 cipher"""
    encoded_text = encodeRot13(data.text)
    return {
        "result": encoded_text,
        "user": user["username"]
    }

@app.get("/api/user-info")
@limiter.limit("15/minute")
def get_user_info(request: Request, user = Depends(get_current_user)):
    """Get current user details"""
    return {
        "message": f"Hello {user['username']}!",
        "user_id": user["id"],
        "username": user["username"]
    }

if __name__ == "__main__":
    print("Starting ROT13 API server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
