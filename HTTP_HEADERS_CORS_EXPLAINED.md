# HTTP Headers & CORS - Complete Technical Guide

## 🌐 **HTTP Headers Overview**

HTTP headers are **key-value pairs** sent between client and server to provide essential information about the request or response. They control caching, authentication, content type, and security policies.

### **Header Structure**
```
Header-Name: Header-Value
Content-Type: application/json
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

---

## 📨 **Request Headers (Client → Server)**

### **1. Authentication Headers**

#### **Authorization Header**
```http
Authorization: Bearer <token>
Authorization: Basic <base64-encoded-credentials>
Authorization: Digest <digest-response>
```

**In Our ROT13 API:**
```http
POST /api/rot13
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Content-Type: application/json

{
  "text": "HELLO WORLD"
}
```

**FastAPI Extraction:**
```python
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    # Automatically extracts token from Authorization: Bearer <token>
    return verify_token(token)
```

### **2. Content Headers**

#### **Content-Type**
Specifies the media type of the request body:
```http
Content-Type: application/json          # JSON data
Content-Type: application/x-www-form-urlencoded  # Form data
Content-Type: multipart/form-data       # File uploads
Content-Type: text/plain                # Plain text
```

#### **Content-Length**
Specifies the size of the request body in bytes:
```http
Content-Length: 25
```

#### **Accept**
Specifies what content types the client can handle:
```http
Accept: application/json
Accept: text/html, application/json, */*
```

### **3. Client Information Headers**

#### **User-Agent**
Identifies the client application:
```http
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
User-Agent: curl/7.68.0
User-Agent: PostmanRuntime/7.28.4
```

#### **Host**
Specifies the domain name of the server:
```http
Host: api.example.com
Host: localhost:8000
```

### **4. Custom Headers**
```http
X-API-Key: your-api-key-here
X-Request-ID: 123e4567-e89b-12d3-a456-426614174000
X-Client-Version: 1.2.3
```

---

## 📤 **Response Headers (Server → Client)**

### **1. Status and Content Headers**

#### **Content-Type**
```http
Content-Type: application/json; charset=utf-8
```

#### **Content-Length**
```http
Content-Length: 156
```

### **2. Security Headers**

#### **X-Content-Type-Options**
Prevents MIME type sniffing:
```http
X-Content-Type-Options: nosniff
```

#### **X-Frame-Options**
Prevents clickjacking attacks:
```http
X-Frame-Options: DENY
X-Frame-Options: SAMEORIGIN
```

#### **X-XSS-Protection**
Enables XSS filtering:
```http
X-XSS-Protection: 1; mode=block
```

### **3. Caching Headers**

#### **Cache-Control**
```http
Cache-Control: no-cache, no-store, must-revalidate
Cache-Control: public, max-age=3600
```

#### **ETag**
```http
ETag: "33a64df551425fcc55e4d42a148795d9f25f89d4"
```

---

## 🔒 **CORS (Cross-Origin Resource Sharing)**

CORS is a **security mechanism** that allows or restricts web pages from one domain to access resources from another domain. It's enforced by browsers to prevent malicious cross-origin requests.

### **Same-Origin Policy**

**Same Origin:** Same protocol, domain, and port
```
https://api.example.com:443/users    ← Same origin
https://api.example.com:443/posts    ← Same origin

http://api.example.com:443/users     ← Different protocol (http vs https)
https://other.example.com:443/users  ← Different domain
https://api.example.com:8080/users   ← Different port
```

### **CORS Headers**

#### **1. Preflight Request (Browser → Server)**
For complex requests, browsers send a preflight OPTIONS request:
```http
OPTIONS /api/rot13
Origin: https://myapp.com
Access-Control-Request-Method: POST
Access-Control-Request-Headers: Authorization, Content-Type
```

#### **2. Preflight Response (Server → Browser)**
```http
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://myapp.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Authorization, Content-Type
Access-Control-Max-Age: 86400
```

#### **3. Actual Request**
```http
POST /api/rot13
Origin: https://myapp.com
Authorization: Bearer <token>
Content-Type: application/json
```

#### **4. Actual Response**
```http
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://myapp.com
Content-Type: application/json

{
  "result": "URYYB JBEYQ"
}
```

### **CORS Headers Explained**

#### **Access-Control-Allow-Origin**
Specifies which origins can access the resource:
```http
Access-Control-Allow-Origin: *                    # Allow all origins (not secure)
Access-Control-Allow-Origin: https://myapp.com    # Allow specific origin
Access-Control-Allow-Origin: null                 # Allow no origins
```

#### **Access-Control-Allow-Methods**
Specifies allowed HTTP methods:
```http
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
```

#### **Access-Control-Allow-Headers**
Specifies allowed request headers:
```http
Access-Control-Allow-Headers: Authorization, Content-Type, X-Requested-With
```

#### **Access-Control-Allow-Credentials**
Allows cookies and credentials:
```http
Access-Control-Allow-Credentials: true
```

#### **Access-Control-Max-Age**
Specifies how long preflight results can be cached:
```http
Access-Control-Max-Age: 86400  # 24 hours
```

---

## 🚀 **CORS in FastAPI**

### **Adding CORS to Our ROT13 API**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://myapp.com", "http://localhost:3000"],  # Specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)
```

### **CORS Configuration Options**

#### **Development Setup (Permissive)**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=False,  # Don't allow credentials with wildcard
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)
```

#### **Production Setup (Restrictive)**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://myapp.com",
        "https://admin.myapp.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=600,  # Cache preflight for 10 minutes
)
```

---

## 🔍 **Common CORS Scenarios**

### **Scenario 1: Simple Request**
**No preflight needed** for simple requests:
- Methods: GET, HEAD, POST
- Headers: Accept, Accept-Language, Content-Language, Content-Type (limited values)
- Content-Type: application/x-www-form-urlencoded, multipart/form-data, text/plain

```javascript
// Simple request - no preflight
fetch('http://localhost:8000/health', {
  method: 'GET'
});
```

### **Scenario 2: Complex Request**
**Preflight required** for complex requests:
- Custom headers (Authorization)
- Content-Type: application/json
- Methods: PUT, DELETE, PATCH

```javascript
// Complex request - triggers preflight
fetch('http://localhost:8000/api/rot13', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer token',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({text: 'HELLO'})
});
```

### **Scenario 3: Credentials Request**
```javascript
// Request with credentials (cookies, auth headers)
fetch('http://localhost:8000/api/rot13', {
  method: 'POST',
  credentials: 'include',  // Include cookies
  headers: {
    'Authorization': 'Bearer token',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({text: 'HELLO'})
});
```

---

## 🛠️ **Debugging CORS Issues**

### **Common CORS Errors**

#### **1. "Access to fetch blocked by CORS policy"**
```
Access to fetch at 'http://localhost:8000/api/rot13' from origin 'http://localhost:3000' 
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present.
```

**Solution:** Add CORS middleware with correct origins:
```python
allow_origins=["http://localhost:3000"]
```

#### **2. "CORS preflight request failed"**
```
Access to fetch blocked by CORS policy: Response to preflight request doesn't pass 
access control check: No 'Access-Control-Allow-Origin' header is present.
```

**Solution:** Ensure OPTIONS method is handled:
```python
allow_methods=["GET", "POST", "OPTIONS"]
```

#### **3. "Credentials not allowed"**
```
Access to fetch blocked by CORS policy: The value of the 'Access-Control-Allow-Origin' 
header must not be the wildcard '*' when the request's credentials mode is 'include'.
```

**Solution:** Use specific origins with credentials:
```python
allow_origins=["http://localhost:3000"],  # Not "*"
allow_credentials=True
```

### **CORS Debugging Tools**

#### **Browser Developer Tools**
1. Open Network tab
2. Look for OPTIONS preflight requests
3. Check response headers
4. Verify Access-Control-* headers

#### **curl Testing**
```bash
# Test preflight request
curl -X OPTIONS http://localhost:8000/api/rot13 \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Authorization, Content-Type" \
  -v

# Test actual request
curl -X POST http://localhost:8000/api/rot13 \
  -H "Origin: http://localhost:3000" \
  -H "Authorization: Bearer token" \
  -H "Content-Type: application/json" \
  -d '{"text": "HELLO"}' \
  -v
```

---

## 🔐 **Security Considerations**

### **CORS Security Best Practices**

#### **1. Avoid Wildcard Origins in Production**
```python
# ❌ Insecure for production
allow_origins=["*"]

# ✅ Secure - specific origins
allow_origins=["https://myapp.com", "https://admin.myapp.com"]
```

#### **2. Be Restrictive with Methods**
```python
# ❌ Too permissive
allow_methods=["*"]

# ✅ Only what you need
allow_methods=["GET", "POST"]
```

#### **3. Limit Headers**
```python
# ❌ Too broad
allow_headers=["*"]

# ✅ Specific headers only
allow_headers=["Authorization", "Content-Type"]
```

#### **4. Credentials Handling**
```python
# ✅ Only when necessary
allow_credentials=True
allow_origins=["https://myapp.com"]  # Must be specific, not "*"
```

### **CORS vs CSRF Protection**

CORS doesn't protect against CSRF attacks from allowed origins. Use additional protection:
```python
# Add CSRF protection
from fastapi_csrf_protect import CsrfProtect

@app.post("/api/rot13")
def encode_text(request: Request, csrf_protect: CsrfProtect = Depends()):
    csrf_protect.validate_csrf(request)
    # ... rest of endpoint
```

---

## 🎯 **Interview Questions & Answers**

### **Q: What's the difference between CORS and authentication?**
**A:** CORS controls which domains can make requests (browser security), authentication verifies user identity. CORS happens before authentication - if CORS fails, the request never reaches your auth logic.

### **Q: Why do some requests trigger preflight and others don't?**
**A:** Simple requests (GET, POST with basic content types) don't need preflight. Complex requests (custom headers, JSON content, PUT/DELETE methods) trigger preflight to check permissions first.

### **Q: Can you bypass CORS?**
**A:** CORS is enforced by browsers, not servers. You can bypass it using:
- Server-side requests (no browser involved)
- Browser extensions that disable CORS
- Proxy servers
- But these don't work for regular web applications

### **Q: What happens if you don't handle CORS?**
**A:** Browsers will block cross-origin requests, showing CORS errors in console. Your API will work fine for same-origin requests or server-to-server calls.

### **Q: How do you handle CORS in microservices?**
**A:** Configure CORS at the API gateway level, or use a service mesh. Each service should also handle CORS for direct access during development.

---

## 📋 **Headers in Our ROT13 API**

### **Login Request**
```http
POST /login HTTP/1.1
Host: localhost:8000
Content-Type: application/x-www-form-urlencoded
Content-Length: 35

username=testuser&password=testuser123
```

### **Login Response**
```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 156

{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

### **ROT13 Request**
```http
POST /api/rot13 HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Content-Type: application/json
Content-Length: 25

{
  "text": "HELLO WORLD"
}
```

### **ROT13 Response**
```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 45

{
  "result": "URYYB JBEYQ",
  "user": "testuser"
}
```

This comprehensive guide covers everything you need to understand HTTP headers and CORS for your interview, with practical examples from web development and your ROT13 API.