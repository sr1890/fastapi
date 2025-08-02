# ROT13 API with JWT Authentication & Rate Limiting - Interview Overview

## Application Overview

This is a **ROT13 text transformation API** built with **FastAPI** and secured with **JWT authentication** and **rate limiting**. ROT13 is a simple letter substitution cipher that replaces each letter with the letter 13 positions after it in the alphabet.

### What the Application Does
- **Transforms text** using ROT13 cipher (A→N, B→O, C→P, etc.)
- **Authenticates users** with JWT tokens
- **Protects endpoints** requiring valid authentication
- **Rate limits requests** to prevent abuse and ensure fair usage
- **Provides user context** in responses

## Architecture & File Structure

```
rot13-fastapi/
├── config.py              # JWT configuration
├── users.py               # User storage
├── schemas.py             # Data models
├── oauth2.py              # JWT token handling
├── auth_endpoints.py      # Login endpoint
├── rate_limiter.py        # Rate limiting configuration
├── main.py                # Main API with rate limits and CORS
├── models.py              # Request/Response models
├── utils.py               # ROT13 logic
├── test_rate_limiting.py  # Rate limiting tests
└── requirements.txt       # Dependencies (includes slowapi)
```

## Authentication Flow

### 1. **User Login Process**
```
Client → POST /login (username/password) → Server validates → JWT token returned
```

### 2. **Protected Request Process**
```
Client → Request with Bearer token → Server validates token → Access granted/denied
```

### 3. **Token Validation Steps**
1. Extract token from Authorization header
2. Decode JWT using secret key
3. Verify token signature and expiration
4. Extract username from token payload
5. Look up user in storage
6. Return user context or error

## Code Walkthrough

### 1. **User Storage** ([`users.py`](users.py:1))
```python
USERS = {
    "testuser": {"id": 1, "username": "testuser", "password": "testpass123"},
    "admin": {"id": 2, "username": "admin", "password": "admin123"}
}

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if user and user["password"] == password:
        return user
    return None
```
**Interview Point**: Simple dictionary storage for demo purposes. In production, would use database with hashed passwords.

### 2. **JWT Configuration** ([`config.py`](config.py:1))
```python
class Settings(BaseSettings):
    secret_key: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
```
**Interview Point**: Uses Pydantic settings for configuration management with environment variable support.

### 3. **JWT Token Operations** ([`oauth2.py`](oauth2.py:1))
```python
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

def verify_token(token: str):
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    username = payload.get("username")
    return username

def get_current_user(token: str = Depends(oauth2_scheme)):
    username = verify_token(token)
    user = get_user(username)
    return user
```
**Interview Point**: Clean separation of concerns - token creation, validation, and user extraction.

### 4. **Login Endpoint** ([`auth_endpoints.py`](auth_endpoints.py:1))
```python
@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Wrong username or password")
    
    access_token = create_access_token(data={"username": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}
```
**Interview Point**: Standard OAuth2 password flow implementation.

### 5. **Protected Endpoints** ([`main.py`](main.py:1))
```python
@app.post("/api/rot13")
def transform_text(request: TextRequest, current_user = Depends(get_current_user)):
    result = encodeRot13(request.text)
    return {"result": result, "user": current_user["username"]}
```
**Interview Point**: FastAPI dependency injection automatically handles authentication.

### 6. **Rate Limiting Implementation** ([`rate_limiter.py`](rate_limiter.py:1))
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

# Simple rate limiter using client IP
limiter = Limiter(key_func=get_remote_address)

def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Simple handler for rate limit errors"""
    return JSONResponse(
        status_code=429,
        content={"error": "Too many requests. Please try again later."}
    )
```
**Interview Point**: Clean, simple rate limiting using IP addresses as keys with user-friendly error messages.

### 7. **Rate Limited Endpoints** ([`main.py`](main.py:20))
```python
@app.post("/api/rot13")
@limiter.limit("20/minute")
def encode_text(request: Request, data: TextRequest, user = Depends(get_current_user)):
    """Encode text using ROT13 cipher"""
    encoded_text = encodeRot13(data.text)
    return {"result": encoded_text, "user": user["username"]}
```
**Interview Point**: Decorator-based rate limiting is clean and easy to configure per endpoint.

## API Endpoints

### Rate Limits Applied
| Endpoint | Rate Limit | Purpose |
|----------|------------|---------|
| `/login` | 5/minute | Prevent brute force attacks |
| `/` | 10/minute | API info, moderate usage |
| `/health` | 30/minute | Health checks need higher limit |
| `/api/rot13` | 20/minute | Main feature, good for normal use |
| `/api/user-info` | 15/minute | User data, moderate usage |

### Public Endpoints
- `GET /` - API information
- `GET /health` - Health check
- `POST /login` - User authentication

### Protected Endpoints (Require JWT Token)
- `POST /api/rot13` - Transform text using ROT13
- `GET /api/user-info` - Get current user information

## Testing the Application

### 1. **Start Server**
```bash
python main.py
```

### 2. **Login to Get Token**
```bash
curl -X POST "http://localhost:8000/login" \
     -d "username=testuser&password=testpass123"
```
**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. **Use Token for Protected Endpoint**
```bash
curl -X POST "http://localhost:8000/api/rot13" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"text": "HELLO WORLD"}'
```
**Response:**
```json
{
  "result": "URYYB JBEYQ",
  "user": "testuser"
}
```

## Key Interview Questions & Answers

### Q: "Why did you choose JWT over session-based authentication?"
**A:** JWT is stateless, scalable, and works well with APIs. No server-side session storage needed, tokens can be validated independently, and it's mobile-friendly.

### Q: "How do you handle token expiration?"
**A:** Tokens expire after 30 minutes (configurable). Client gets 401 error and needs to re-authenticate. In production, would implement refresh tokens.

### Q: "What security measures are implemented?"
**A:**
- JWT tokens are signed with secret key
- Tokens have expiration time
- Bearer token format in Authorization header
- Rate limiting to prevent abuse and brute force attacks
- CORS middleware for secure cross-origin requests
- Proper HTTP status codes for errors
- Input validation with Pydantic models

### Q: "How does the rate limiting work?"
**A:** Uses `slowapi` library to track requests per IP address. Each endpoint has specific limits (login: 5/min, main API: 20/min, etc.). When limits are exceeded, returns 429 status with user-friendly error message. Prevents brute force attacks and ensures fair API usage.

### Q: "Why different rate limits for different endpoints?"
**A:**
- **Login (5/min)**: Strictest limit to prevent credential attacks
- **Main API (20/min)**: Moderate limit for normal usage
- **Health check (30/min)**: Higher limit for monitoring systems
- **Info endpoints (10-15/min)**: Balanced for typical usage patterns

### Q: "How would you scale this for production?"
**A:**
- Database integration (PostgreSQL)
- Password hashing (bcrypt)
- Refresh token mechanism
- Redis backend for rate limiting (distributed systems)
- HTTPS enforcement
- Environment-based configuration
- User roles and permissions
- Token blacklisting for logout
- Per-user rate limiting instead of just IP-based

### Q: "Explain the dependency injection pattern used"
**A:** FastAPI's `Depends()` automatically handles authentication. When `current_user = Depends(get_current_user)` is used, FastAPI:
1. Extracts token from request
2. Calls `get_current_user()` function
3. Validates token and returns user
4. Injects user into endpoint function
5. Returns 401 if validation fails

### Q: "How does ROT13 work?"
**A:** ROT13 shifts each letter 13 positions in the alphabet. A→N, B→O, etc. It's symmetric - applying ROT13 twice returns original text. Used for simple obfuscation, not real encryption.

## Technical Highlights

- **Clean Architecture**: Separation of concerns across modules
- **Type Safety**: Pydantic models for request/response validation
- **Rate Limiting**: IP-based request limiting with configurable thresholds
- **CORS Support**: Cross-Origin Resource Sharing for frontend integration
- **Error Handling**: Proper HTTP status codes and user-friendly error messages
- **Documentation**: FastAPI auto-generates interactive API docs
- **Testing**: Easy to test with curl or dedicated test scripts
- **Maintainable**: Simple, readable code structure with clear naming

## Testing Rate Limiting

```bash
# Test rate limiting functionality
python test_rate_limiting.py
```

This implementation demonstrates solid understanding of:
- REST API design
- JWT authentication
- Rate limiting and abuse prevention
- FastAPI framework
- Python best practices
- Security considerations
- Clean code principles
- Production-ready features