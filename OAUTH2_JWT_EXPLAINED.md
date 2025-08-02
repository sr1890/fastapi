# OAuth2 & JWT - Complete Technical Guide

## 🔐 **OAuth2 Framework Overview**

OAuth2 is an **authorization framework** that enables applications to obtain limited access to user accounts. It works by delegating user authentication to the service that hosts the user account and authorizing third-party applications to access that user account.

### **Key OAuth2 Concepts**

#### **1. Roles in OAuth2**
- **Resource Owner**: The user who owns the data (e.g., you on Facebook)
- **Client**: The application requesting access (e.g., a mobile app)
- **Authorization Server**: Issues access tokens (e.g., Google's auth server)
- **Resource Server**: Hosts the protected resources (e.g., Google Drive API)

#### **2. OAuth2 Grant Types**

**Authorization Code Flow** (Most Secure)
```
1. Client redirects user to Authorization Server
2. User authenticates and grants permission
3. Authorization Server redirects back with authorization code
4. Client exchanges code for access token
5. Client uses token to access resources
```

**Client Credentials Flow** (Used in our ROT13 API)
```
1. Client authenticates directly with Authorization Server
2. Authorization Server issues access token
3. Client uses token for API requests
```

### **How OAuth2 Works in Our ROT13 API**

```python
# Step 1: Client sends credentials
POST /login
Content-Type: application/x-www-form-urlencoded
username=testuser&password=testuser123

# Step 2: Server validates and returns token
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}

# Step 3: Client uses token for protected resources
POST /api/rot13
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

---

## 🎫 **JWT (JSON Web Tokens) Deep Dive**

JWT is a **compact, URL-safe means of representing claims** to be transferred between two parties. It's a standard (RFC 7519) for securely transmitting information.

### **JWT Structure**

A JWT consists of three parts separated by dots (`.`):
```
header.payload.signature
```

#### **1. Header**
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```
- **alg**: Algorithm used for signing (HMAC SHA256)
- **typ**: Token type (JWT)

#### **2. Payload (Claims)**
```json
{
  "username": "testuser",
  "exp": 1640995200,
  "iat": 1640991600
}
```
- **username**: Custom claim (user identifier)
- **exp**: Expiration time (Unix timestamp)
- **iat**: Issued at time (Unix timestamp)

#### **3. Signature**
```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  secret_key
)
```

### **Complete JWT Example**

**Raw JWT:**
```
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6InRlc3R1c2VyIiwiZXhwIjoxNjQwOTk1MjAwfQ.signature_hash_here
```

**Decoded:**
```json
// Header
{
  "typ": "JWT",
  "alg": "HS256"
}

// Payload
{
  "username": "testuser",
  "exp": 1640995200
}

// Signature (verified with secret key)
```

### **JWT in Our Code**

#### **Token Creation** (`oauth2.py`)
```python
def create_access_token(data: dict):
    to_encode = data.copy()
    # Add expiration time (30 minutes from now)
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    
    # Create JWT with HS256 algorithm
    token = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    return token
```

#### **Token Verification** (`oauth2.py`)
```python
def verify_token(token: str):
    try:
        # Decode and verify signature
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        username = payload.get("username")
        
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

---

## 🔄 **OAuth2 vs JWT Relationship**

### **Common Misconception**
- **OAuth2** is a **framework** (defines how to get tokens)
- **JWT** is a **token format** (defines what tokens look like)

### **How They Work Together**
```
OAuth2 Framework:     "How do I get a token?"
JWT Format:          "What does the token contain?"

OAuth2 + JWT:        "Get a JWT token using OAuth2 flow"
```

### **In Our ROT13 API:**
1. **OAuth2 Flow**: Client credentials grant type
2. **JWT Format**: Access tokens are JWTs containing user info
3. **Security**: HMAC SHA256 signature with secret key

---

## 🛡️ **Security Considerations**

### **JWT Security Best Practices**

#### **1. Secret Key Management**
```python
# ❌ Bad: Hardcoded secret
SECRET_KEY = "my-secret-123"

# ✅ Good: Environment variable
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
```

#### **2. Token Expiration**
```python
# ✅ Short-lived tokens (30 minutes)
expire = datetime.now(timezone.utc) + timedelta(minutes=30)
```

#### **3. Algorithm Specification**
```python
# ✅ Explicitly specify algorithm
jwt.decode(token, secret_key, algorithms=["HS256"])
```

### **Common JWT Vulnerabilities**

#### **1. Algorithm Confusion Attack**
```python
# ❌ Vulnerable: Accepts any algorithm
jwt.decode(token, secret_key)

# ✅ Secure: Specifies allowed algorithms
jwt.decode(token, secret_key, algorithms=["HS256"])
```

#### **2. Secret Key Exposure**
- Never commit secrets to version control
- Use environment variables or secret management
- Rotate keys regularly

#### **3. Token Storage**
- **Client-side**: Store in memory or secure storage
- **Never**: Store in localStorage for sensitive apps
- **Consider**: HttpOnly cookies for web apps

---

## 🔍 **JWT vs Other Token Types**

### **JWT vs Opaque Tokens**

| Aspect | JWT | Opaque Token |
|--------|-----|--------------|
| **Format** | JSON with claims | Random string |
| **Validation** | Cryptographic signature | Database lookup |
| **Size** | Larger (contains data) | Smaller |
| **Stateless** | Yes | No (requires server state) |
| **Revocation** | Difficult | Easy |
| **Performance** | Fast validation | Requires DB query |

### **When to Use JWT**
✅ **Good for:**
- Stateless authentication
- Microservices architecture
- Short-lived tokens
- Cross-domain authentication

❌ **Avoid for:**
- Long-lived sessions
- Frequent revocation needs
- Sensitive data in payload
- Large payload requirements

---

## 🚀 **Implementation in FastAPI**

### **Complete Flow in Our Code**

#### **1. Login Endpoint** (`auth_endpoints.py`)
```python
@router.post("/login", response_model=Token)
def user_login(credentials: OAuth2PasswordRequestForm = Depends()):
    # Validate user credentials
    user = authenticate_user(credentials.username, credentials.password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create JWT token
    token = create_access_token(data={"username": user["username"]})
    
    return {"access_token": token, "token_type": "bearer"}
```

#### **2. Protected Endpoint** (`rot13_api.py`)
```python
@app.post("/api/rot13")
def encode_text(data: TextRequest, user = Depends(get_current_user)):
    # user is automatically extracted from JWT token
    encoded_text = encodeRot13(data.text)
    return {"result": encoded_text, "user": user["username"]}
```

#### **3. Token Extraction** (`oauth2.py`)
```python
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    # Automatically extracts token from Authorization header
    username = verify_token(token)
    user = get_user(username)
    return user
```

---

## 🎯 **Interview Questions & Answers**

### **Q: What's the difference between authentication and authorization?**
**A:** Authentication verifies "who you are" (login), authorization determines "what you can do" (permissions). JWT handles authentication, OAuth2 handles authorization.

### **Q: Why use JWT over sessions?**
**A:** JWT is stateless (no server storage), scalable across multiple servers, and contains user info directly. Sessions require server-side storage and don't work well in distributed systems.

### **Q: How do you handle JWT expiration?**
**A:** Implement refresh tokens for long-lived access, or require re-authentication. Our API uses short-lived tokens (30 min) for security.

### **Q: Can JWT be revoked?**
**A:** Not easily - they're stateless. Solutions include token blacklists, short expiration times, or switching to opaque tokens for revocation-critical scenarios.

### **Q: What's in the JWT signature?**
**A:** HMAC hash of header + payload using secret key. It prevents tampering - any change to header/payload invalidates the signature.

---

## 🔧 **Debugging JWT Issues**

### **Common Problems & Solutions**

#### **1. "Invalid Token" Error**
```python
# Check: Token format, expiration, signature
try:
    payload = jwt.decode(token, secret_key, algorithms=["HS256"])
    print(f"Token valid, expires: {payload.get('exp')}")
except jwt.ExpiredSignatureError:
    print("Token expired")
except jwt.InvalidTokenError:
    print("Invalid token format or signature")
```

#### **2. Token Not Found**
```python
# Check: Authorization header format
# Correct: "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
# Wrong: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." (missing Bearer)
```

#### **3. Clock Skew Issues**
```python
# Add leeway for time differences between servers
jwt.decode(token, secret_key, algorithms=["HS256"], leeway=10)
```

This comprehensive guide covers everything you need to understand and explain OAuth2 and JWT concepts during your interview, with practical examples from your ROT13 API implementation.