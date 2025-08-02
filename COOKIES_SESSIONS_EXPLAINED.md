# Cookies & Session Management - Complete Technical Guide

## 🍪 **HTTP Cookies Overview**

HTTP cookies are **small pieces of data** stored by the web browser and sent back to the server with every request. They enable stateful communication over the stateless HTTP protocol.

### **Cookie Structure**
```
Set-Cookie: name=value; Domain=example.com; Path=/; Expires=Wed, 09 Jun 2021 10:18:14 GMT; Secure; HttpOnly; SameSite=Strict
```

---

## 🔧 **Cookie Mechanics**

### **1. Cookie Creation (Server → Browser)**

#### **Basic Cookie**
```http
HTTP/1.1 200 OK
Set-Cookie: session_id=abc123
Content-Type: text/html

<html>...</html>
```

#### **Cookie with Attributes**
```http
HTTP/1.1 200 OK
Set-Cookie: auth_token=xyz789; Domain=api.example.com; Path=/; Max-Age=3600; Secure; HttpOnly; SameSite=Strict
Content-Type: application/json
```

### **2. Cookie Transmission (Browser → Server)**
```http
GET /api/user-info HTTP/1.1
Host: api.example.com
Cookie: session_id=abc123; auth_token=xyz789
```

### **3. Cookie Attributes Explained**

#### **Domain**
Specifies which hosts can receive the cookie:
```http
Set-Cookie: token=abc123; Domain=example.com
# Sent to: example.com, api.example.com, www.example.com
# NOT sent to: other.com, evil.com
```

#### **Path**
Specifies which paths can receive the cookie:
```http
Set-Cookie: admin_token=xyz; Path=/admin
# Sent to: /admin, /admin/users, /admin/settings
# NOT sent to: /, /api, /public
```

#### **Expires / Max-Age**
Controls cookie lifetime:
```http
Set-Cookie: temp=123; Expires=Wed, 09 Jun 2021 10:18:14 GMT
Set-Cookie: session=456; Max-Age=3600  # 1 hour from now
```

#### **Secure**
Cookie only sent over HTTPS:
```http
Set-Cookie: sensitive=data; Secure
# Only transmitted over encrypted connections
```

#### **HttpOnly**
Prevents JavaScript access (XSS protection):
```http
Set-Cookie: session=abc123; HttpOnly
# Cannot be accessed via document.cookie
```

#### **SameSite**
Controls cross-site request behavior:
```http
Set-Cookie: csrf_token=xyz; SameSite=Strict   # Never sent cross-site
Set-Cookie: tracking=123; SameSite=Lax        # Sent on top-level navigation
Set-Cookie: embed=456; SameSite=None; Secure  # Always sent (requires Secure)
```

---

## 🗂️ **Session Management**

### **Session vs Cookies**

| Aspect | Cookies | Sessions |
|--------|---------|----------|
| **Storage** | Browser (client-side) | Server-side |
| **Size Limit** | ~4KB per cookie | Limited by server memory/storage |
| **Security** | Visible to client | Hidden from client |
| **Persistence** | Can persist after browser close | Usually temporary |
| **Performance** | Sent with every request | Requires server lookup |

### **Session Implementation Patterns**

#### **1. Server-Side Sessions**
```python
# Session stored on server, cookie contains session ID
sessions = {}  # In-memory store (use Redis/database in production)

def create_session(user_id):
    session_id = generate_random_id()
    sessions[session_id] = {
        'user_id': user_id,
        'created_at': datetime.now(),
        'data': {}
    }
    return session_id

def get_session(session_id):
    return sessions.get(session_id)
```

#### **2. Client-Side Sessions (JWT)**
```python
# Session data stored in JWT token (our ROT13 API approach)
def create_jwt_session(user_data):
    token = jwt.encode({
        'user_id': user_data['id'],
        'username': user_data['username'],
        'exp': datetime.utcnow() + timedelta(hours=1)
    }, SECRET_KEY)
    return token
```

---

## 🔐 **Cookie-Based Authentication**

### **Traditional Cookie Auth Flow**

#### **1. Login Process**
```python
from fastapi import FastAPI, Response, Cookie
from typing import Optional

@app.post("/login")
def login(credentials: LoginForm, response: Response):
    user = authenticate_user(credentials.username, credentials.password)
    if user:
        session_id = create_session(user['id'])
        response.set_cookie(
            key="session_id",
            value=session_id,
            max_age=3600,  # 1 hour
            httponly=True,  # Prevent XSS
            secure=True,    # HTTPS only
            samesite="strict"  # CSRF protection
        )
        return {"message": "Login successful"}
    raise HTTPException(status_code=401, detail="Invalid credentials")
```

#### **2. Protected Endpoint**
```python
@app.get("/api/user-info")
def get_user_info(session_id: Optional[str] = Cookie(None)):
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    return {"user_id": session['user_id']}
```

#### **3. Logout Process**
```python
@app.post("/logout")
def logout(response: Response, session_id: Optional[str] = Cookie(None)):
    if session_id:
        # Remove session from server
        sessions.pop(session_id, None)
        # Clear cookie
        response.delete_cookie("session_id")
    return {"message": "Logged out"}
```

---

## 🆚 **Cookies vs JWT Comparison**

### **Cookie-Based Auth**
```python
# Server stores session data
@app.post("/login")
def login(response: Response):
    session_id = create_session(user_id)
    response.set_cookie("session_id", session_id, httponly=True)
    return {"status": "logged in"}

@app.get("/protected")
def protected(session_id: str = Cookie(None)):
    session = get_session(session_id)  # Database lookup
    return {"user": session['user_id']}
```

### **JWT-Based Auth (Our ROT13 API)**
```python
# Client stores token data
@app.post("/login")
def login():
    token = create_access_token({"username": user["username"]})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/protected")
def protected(user = Depends(get_current_user)):  # No database lookup
    return {"user": user["username"]}
```

### **Comparison Table**

| Feature | Cookies + Sessions | JWT Tokens |
|---------|-------------------|------------|
| **Storage** | Server-side | Client-side |
| **Scalability** | Requires shared storage | Stateless |
| **Security** | Server controls data | Client holds data |
| **Revocation** | Easy (delete session) | Difficult |
| **Size** | Small cookie (session ID) | Larger token |
| **Performance** | Database lookup needed | No lookup needed |
| **CSRF Protection** | Vulnerable (needs CSRF tokens) | Resistant (manual header) |
| **XSS Protection** | Good (HttpOnly cookies) | Vulnerable (localStorage) |

---

## 🛡️ **Security Considerations**

### **Cookie Security Best Practices**

#### **1. Secure Attribute**
```python
# ✅ Always use Secure in production
response.set_cookie("session", value, secure=True)

# ❌ Never in production without HTTPS
response.set_cookie("session", value, secure=False)
```

#### **2. HttpOnly Attribute**
```python
# ✅ Prevents XSS attacks
response.set_cookie("session", value, httponly=True)

# ❌ Vulnerable to XSS
response.set_cookie("session", value, httponly=False)
```

#### **3. SameSite Attribute**
```python
# ✅ Strict CSRF protection
response.set_cookie("session", value, samesite="strict")

# ✅ Balanced protection (allows some cross-site)
response.set_cookie("session", value, samesite="lax")

# ⚠️ Use with caution
response.set_cookie("session", value, samesite="none", secure=True)
```

#### **4. Proper Expiration**
```python
# ✅ Set reasonable expiration
response.set_cookie("session", value, max_age=3600)  # 1 hour

# ❌ Never expires (security risk)
response.set_cookie("session", value)  # Session cookie
```

### **Common Cookie Vulnerabilities**

#### **1. Session Fixation**
```python
# ❌ Vulnerable: Reusing session ID after login
def login():
    if authenticate_user():
        # Don't reuse existing session_id
        return {"status": "logged in"}

# ✅ Secure: Generate new session ID after login
def login():
    if authenticate_user():
        old_session_id = request.cookies.get("session_id")
        if old_session_id:
            sessions.pop(old_session_id, None)  # Invalidate old session
        
        new_session_id = create_session(user_id)
        response.set_cookie("session_id", new_session_id)
```

#### **2. Session Hijacking**
```python
# ✅ Mitigations
def validate_session(session_id: str, request: Request):
    session = get_session(session_id)
    if not session:
        return None
    
    # Check IP address (optional, can break mobile users)
    if session.get('ip') != request.client.host:
        # Log suspicious activity
        pass
    
    # Check User-Agent (basic fingerprinting)
    if session.get('user_agent') != request.headers.get('user-agent'):
        # Log suspicious activity
        pass
    
    return session
```

#### **3. CSRF Attacks**
```python
# ✅ CSRF Protection with cookies
from fastapi_csrf_protect import CsrfProtect

@app.post("/api/transfer-money")
def transfer_money(
    request: Request,
    csrf_protect: CsrfProtect = Depends(),
    session_id: str = Cookie(None)
):
    csrf_protect.validate_csrf(request)  # Validate CSRF token
    session = get_session(session_id)
    # ... process transfer
```

---

## 🔄 **Session Storage Options**

### **1. In-Memory Storage**
```python
# Simple but not scalable
sessions = {}

def create_session(user_id):
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        'user_id': user_id,
        'created_at': datetime.now()
    }
    return session_id
```

### **2. Redis Storage**
```python
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def create_session(user_id):
    session_id = str(uuid.uuid4())
    session_data = {
        'user_id': user_id,
        'created_at': datetime.now().isoformat()
    }
    redis_client.setex(
        f"session:{session_id}",
        3600,  # 1 hour expiration
        json.dumps(session_data)
    )
    return session_id

def get_session(session_id):
    data = redis_client.get(f"session:{session_id}")
    return json.loads(data) if data else None
```

### **3. Database Storage**
```python
from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Session(Base):
    __tablename__ = "sessions"
    
    session_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)

def create_session(user_id):
    session_id = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(hours=1)
    
    session = Session(
        session_id=session_id,
        user_id=user_id,
        expires_at=expires_at
    )
    db.add(session)
    db.commit()
    return session_id
```

---

## 🌐 **Cookies in Different Contexts**

### **1. Single Page Applications (SPA)**
```javascript
// Frontend (React/Vue/Angular)
// Cookies are automatically sent with requests
fetch('/api/user-info', {
  credentials: 'include'  // Include cookies
});

// No need to manually handle cookies
// Browser automatically sends them
```

### **2. Mobile Applications**
```python
# Mobile apps typically use tokens, not cookies
# But can simulate cookie behavior

@app.post("/mobile-login")
def mobile_login():
    # Return token instead of setting cookie
    token = create_access_token(user_data)
    return {"access_token": token}

# Mobile app stores token and sends in headers
# Authorization: Bearer <token>
```

### **3. Microservices**
```python
# Service A sets cookie
@app.post("/auth/login")
def login(response: Response):
    session_id = create_session(user_id)
    response.set_cookie(
        "session_id", 
        session_id,
        domain=".myapp.com"  # Shared across subdomains
    )

# Service B reads cookie
@app.get("/api/data")
def get_data(session_id: str = Cookie(None)):
    # Validate session (shared session store)
    session = redis_client.get(f"session:{session_id}")
```

---

## 🧪 **Testing Cookies**

### **1. Manual Testing with curl**
```bash
# Login and save cookies
curl -c cookies.txt -X POST http://localhost:8000/login \
  -d "username=testuser&password=password"

# Use saved cookies for subsequent requests
curl -b cookies.txt http://localhost:8000/api/user-info

# Check cookie content
cat cookies.txt
```

### **2. Browser Developer Tools**
```javascript
// View cookies in console
document.cookie

// Set cookie manually
document.cookie = "test=value; path=/; max-age=3600"

// Clear all cookies
document.cookie.split(";").forEach(function(c) { 
  document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/"); 
});
```

### **3. FastAPI Testing**
```python
from fastapi.testclient import TestClient

def test_cookie_auth():
    client = TestClient(app)
    
    # Login
    response = client.post("/login", data={"username": "test", "password": "test"})
    assert response.status_code == 200
    
    # Check if cookie is set
    assert "session_id" in response.cookies
    
    # Use cookie for protected endpoint
    response = client.get("/api/user-info")
    assert response.status_code == 200
```

---

## 🎯 **Interview Questions & Answers**

### **Q: What's the difference between session cookies and persistent cookies?**
**A:** Session cookies expire when the browser closes (no Expires/Max-Age), persistent cookies have an expiration date and survive browser restarts.

### **Q: How do you handle cookie security?**
**A:** Use Secure (HTTPS only), HttpOnly (prevent XSS), SameSite (prevent CSRF), set proper expiration, and validate on server-side.

### **Q: Why choose JWT over cookies?**
**A:** JWT is stateless (better for microservices), doesn't require server-side storage, works across domains easily, but cookies are more secure against XSS and easier to revoke.

### **Q: How do you handle session expiration?**
**A:** Set reasonable expiration times, implement refresh mechanisms, provide clear logout, and clean up expired sessions on the server.

### **Q: What's the cookie size limit?**
**A:** ~4KB per cookie, ~20 cookies per domain. For larger data, store a session ID in the cookie and keep data server-side.

---

## 📋 **Cookie Implementation in Our ROT13 API**

### **Adding Cookie Support**
```python
from fastapi import Cookie, Response
from typing import Optional

# Alternative cookie-based auth for ROT13 API
@app.post("/cookie-login")
def cookie_login(credentials: OAuth2PasswordRequestForm, response: Response):
    user = authenticate_user(credentials.username, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create session instead of JWT
    session_id = create_session(user['id'])
    
    response.set_cookie(
        key="session_id",
        value=session_id,
        max_age=1800,  # 30 minutes
        httponly=True,
        secure=True,   # Use in production with HTTPS
        samesite="strict"
    )
    
    return {"message": "Login successful"}

@app.post("/api/rot13-cookie")
def encode_text_cookie(
    data: TextRequest, 
    session_id: Optional[str] = Cookie(None)
):
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    encoded_text = encodeRot13(data.text)
    return {"result": encoded_text, "user_id": session['user_id']}
```

This comprehensive guide covers everything you need to understand cookies and session management for your interview, including practical implementations and security considerations.