# Pydantic Models - Complete Technical Guide

## 🏗️ **What are Pydantic Models?**

Pydantic models are **Python classes** that define the structure, types, and validation rules for data. They automatically validate incoming data, convert types, and provide clear error messages when validation fails.

### **Why Pydantic in FastAPI?**
- **Automatic Validation**: Validates request/response data automatically
- **Type Safety**: Ensures data matches expected types
- **Documentation**: Auto-generates API documentation
- **Serialization**: Converts between Python objects and JSON
- **Clear Errors**: Provides detailed validation error messages

---

## 📋 **Your Current Models Analysis**

### **1. TextRequest Model** (`models.py`)

```python
from pydantic import BaseModel, field_validator

class TextRequest(BaseModel):
    text: str

    @field_validator('text')
    @classmethod
    def validateText(cls, value):
        if not value:
            raise ValueError("Can't be empty")
        for char in value:
            if not (char.isupper() or char == ' '):
                raise ValueError("Only uppercase letters and spaces allowed")
        return value
```

**What this does:**
- **Defines structure**: Expects a `text` field of type `str`
- **Custom validation**: Only allows uppercase letters and spaces `[A-Z ]`
- **Error handling**: Provides clear error messages for invalid input

**Example usage:**
```python
# ✅ Valid input
request = TextRequest(text="HELLO WORLD")
print(request.text)  # "HELLO WORLD"

# ❌ Invalid input - raises ValidationError
request = TextRequest(text="hello world")  # lowercase not allowed
request = TextRequest(text="")  # empty not allowed
request = TextRequest(text="HELLO123")  # numbers not allowed
```

### **2. TextResponse Model** (`models.py`)

```python
class TextResponse(BaseModel):
    result: str
```

**What this does:**
- **Defines response structure**: Ensures response has `result` field
- **Type safety**: Guarantees `result` is a string
- **Documentation**: Shows expected response format in API docs

### **3. Token Model** (`schemas.py`)

```python
class Token(BaseModel):
    access_token: str
    token_type: str
```

**What this does:**
- **OAuth2 standard**: Follows OAuth2 token response format
- **Required fields**: Both `access_token` and `token_type` must be provided
- **Type validation**: Ensures both fields are strings

### **4. TokenData Model** (`schemas.py`)

```python
from typing import Optional

class TokenData(BaseModel):
    username: Optional[str] = None
```

**What this does:**
- **Optional field**: `username` can be `None` or a string
- **Default value**: Defaults to `None` if not provided
- **JWT payload**: Used for extracting data from JWT tokens

---

## 🔧 **Pydantic Model Components**

### **1. Basic Model Structure**

```python
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class User(BaseModel):
    # Required fields
    id: int
    username: str
    email: str
    
    # Optional fields
    full_name: Optional[str] = None
    is_active: bool = True
    
    # Complex types
    tags: List[str] = []
    created_at: datetime
```

### **2. Field Types**

#### **Basic Types**
```python
class Example(BaseModel):
    text: str           # String
    number: int         # Integer
    price: float        # Float
    is_active: bool     # Boolean
    data: dict          # Dictionary
    items: list         # List
```

#### **Advanced Types**
```python
from typing import Optional, List, Dict, Union
from datetime import datetime
from enum import Enum

class Status(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class AdvancedModel(BaseModel):
    # Optional with default
    status: Status = Status.ACTIVE
    
    # Union types (multiple possible types)
    identifier: Union[int, str]
    
    # Lists with specific types
    scores: List[int]
    
    # Dictionaries with typed values
    metadata: Dict[str, str]
    
    # Datetime
    created_at: datetime
```

### **3. Field Validation**

#### **Built-in Validators**
```python
from pydantic import BaseModel, Field

class UserModel(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    age: int = Field(ge=0, le=120)  # ge = greater equal, le = less equal
    email: str = Field(regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    score: float = Field(gt=0.0, lt=100.0)  # gt = greater than, lt = less than
```

#### **Custom Validators (like your TextRequest)**
```python
from pydantic import BaseModel, field_validator

class TextRequest(BaseModel):
    text: str
    
    @field_validator('text')
    @classmethod
    def validate_text(cls, value):
        # Custom validation logic
        if not value:
            raise ValueError("Text cannot be empty")
        
        if len(value) > 1000:
            raise ValueError("Text too long (max 1000 characters)")
        
        # Your specific validation
        for char in value:
            if not (char.isupper() or char == ' '):
                raise ValueError("Only uppercase letters and spaces allowed")
        
        return value
```

#### **Multiple Field Validation**
```python
from pydantic import BaseModel, model_validator

class PasswordModel(BaseModel):
    password: str
    confirm_password: str
    
    @model_validator(mode='after')
    def validate_passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords don't match")
        return self
```

---

## 🚀 **Models in FastAPI Endpoints**

### **Request Models (Input Validation)**

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class CreateUser(BaseModel):
    username: str
    email: str
    password: str

@app.post("/users/")
def create_user(user: CreateUser):
    # FastAPI automatically:
    # 1. Validates JSON against CreateUser model
    # 2. Converts JSON to Python object
    # 3. Returns 422 error if validation fails
    
    print(f"Creating user: {user.username}")
    return {"message": f"User {user.username} created"}
```

**What happens automatically:**
1. **JSON Parsing**: Converts request body from JSON to Python dict
2. **Validation**: Checks all fields match the model
3. **Type Conversion**: Converts strings to appropriate types
4. **Error Response**: Returns 422 with details if validation fails

### **Response Models (Output Serialization)**

```python
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    # Note: password field excluded for security

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    # Your function can return dict, object, or model instance
    user_data = {
        "id": user_id,
        "username": "testuser",
        "email": "test@example.com",
        "password": "secret123",  # This will be filtered out
        "internal_data": "hidden"  # This will be filtered out
    }
    
    # FastAPI automatically:
    # 1. Filters data to match UserResponse model
    # 2. Validates output data
    # 3. Converts to JSON
    
    return user_data  # Only id, username, email will be returned
```

---

## 🔍 **Your ROT13 API Models in Action**

### **Request Flow with TextRequest**

```python
# 1. Client sends JSON
POST /api/rot13
{
  "text": "HELLO WORLD"
}

# 2. FastAPI receives request
# 3. Pydantic validates against TextRequest model
# 4. Custom validator checks uppercase + spaces only
# 5. If valid, creates TextRequest object
# 6. Passes to your endpoint function

@app.post("/api/rot13")
def encode_text(data: TextRequest, user = Depends(get_current_user)):
    # data.text is guaranteed to be valid uppercase text
    encoded_text = encodeRot13(data.text)
    return {"result": encoded_text, "user": user["username"]}
```

### **Error Handling Example**

```python
# Invalid request
POST /api/rot13
{
  "text": "hello world"  # lowercase not allowed
}

# FastAPI automatically returns:
HTTP 422 Unprocessable Entity
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "text"],
      "msg": "Only uppercase letters and spaces allowed",
      "input": "hello world"
    }
  ]
}
```

---

## 🛠️ **Advanced Model Features**

### **1. Model Configuration**

```python
class ConfiguredModel(BaseModel):
    name: str
    value: int
    
    class Config:
        # Allow extra fields
        extra = "allow"  # or "ignore" or "forbid"
        
        # Validate on assignment
        validate_assignment = True
        
        # Use enum values instead of names
        use_enum_values = True
        
        # Custom JSON encoders
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

### **2. Model Inheritance**

```python
class BaseUser(BaseModel):
    username: str
    email: str
    created_at: datetime

class AdminUser(BaseUser):
    # Inherits all fields from BaseUser
    permissions: List[str]
    is_admin: bool = True

class RegularUser(BaseUser):
    # Inherits all fields from BaseUser
    subscription_type: str = "free"
```

### **3. Nested Models**

```python
class Address(BaseModel):
    street: str
    city: str
    country: str

class User(BaseModel):
    name: str
    address: Address  # Nested model
    
# Usage
user_data = {
    "name": "John Doe",
    "address": {
        "street": "123 Main St",
        "city": "New York",
        "country": "USA"
    }
}
user = User(**user_data)
print(user.address.city)  # "New York"
```

---

## 🔐 **Security with Models**

### **1. Input Sanitization**

```python
class SecureInput(BaseModel):
    username: str = Field(regex=r'^[a-zA-Z0-9_]+$', min_length=3, max_length=20)
    email: str = Field(regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    
    @field_validator('username')
    @classmethod
    def sanitize_username(cls, value):
        # Remove any potentially dangerous characters
        return value.strip().lower()
```

### **2. Response Filtering**

```python
class UserInternal(BaseModel):
    id: int
    username: str
    email: str
    password_hash: str  # Internal use only
    api_key: str        # Internal use only

class UserPublic(BaseModel):
    id: int
    username: str
    # email and sensitive fields excluded

@app.get("/users/{user_id}", response_model=UserPublic)
def get_user_public(user_id: int):
    # Even if you return full internal data,
    # only UserPublic fields will be sent to client
    return get_user_from_db(user_id)
```

---

## 🧪 **Testing Models**

### **1. Unit Testing Validation**

```python
import pytest
from pydantic import ValidationError

def test_text_request_valid():
    # Test valid input
    request = TextRequest(text="HELLO WORLD")
    assert request.text == "HELLO WORLD"

def test_text_request_invalid_lowercase():
    # Test invalid input
    with pytest.raises(ValidationError) as exc_info:
        TextRequest(text="hello world")
    
    assert "Only uppercase letters and spaces allowed" in str(exc_info.value)

def test_text_request_empty():
    with pytest.raises(ValidationError):
        TextRequest(text="")
```

### **2. Testing with FastAPI**

```python
from fastapi.testclient import TestClient

def test_rot13_endpoint():
    client = TestClient(app)
    
    # Test valid request
    response = client.post("/api/rot13", json={"text": "HELLO"})
    assert response.status_code == 200
    assert response.json()["result"] == "URYYB"
    
    # Test invalid request
    response = client.post("/api/rot13", json={"text": "hello"})
    assert response.status_code == 422
```

---

## 🎯 **Interview Questions & Answers**

### **Q: What's the difference between Pydantic models and regular Python classes?**
**A:** Pydantic models provide automatic validation, type conversion, and serialization. Regular classes don't validate data or convert types automatically.

### **Q: How does FastAPI use Pydantic models?**
**A:** FastAPI uses Pydantic models for request validation (input), response serialization (output), and automatic API documentation generation.

### **Q: What happens when validation fails?**
**A:** Pydantic raises a ValidationError, which FastAPI automatically converts to a 422 HTTP response with detailed error information.

### **Q: Can you have optional fields in Pydantic models?**
**A:** Yes, use `Optional[Type]` or `Type | None` (Python 3.10+) with default values like `Optional[str] = None`.

### **Q: How do you validate multiple fields together?**
**A:** Use `@model_validator(mode='after')` to validate the entire model after individual field validation.

---

## 📊 **Model Best Practices**

### **1. Naming Conventions**
```python
# ✅ Good naming
class UserCreateRequest(BaseModel):  # Clear purpose
class UserResponse(BaseModel)        # Clear direction
class TokenData(BaseModel)           # Clear content

# ❌ Avoid generic names
class Data(BaseModel)
class Input(BaseModel)
class Model(BaseModel)
```

### **2. Validation Strategy**
```python
# ✅ Fail fast with clear messages
@field_validator('email')
@classmethod
def validate_email(cls, value):
    if '@' not in value:
        raise ValueError("Invalid email format")
    return value.lower()  # Normalize

# ❌ Silent failures or unclear errors
@field_validator('email')
@classmethod
def validate_email(cls, value):
    return value  # No validation
```

### **3. Documentation**
```python
class WellDocumentedModel(BaseModel):
    """
    Model for user registration requests.
    
    Validates user input and ensures data integrity.
    """
    username: str = Field(
        description="Unique username (3-20 characters)",
        min_length=3,
        max_length=20,
        example="john_doe"
    )
    email: str = Field(
        description="Valid email address",
        example="john@example.com"
    )
```

Your current models in [`models.py`](models.py) and [`schemas.py`](schemas.py) follow these best practices well - they have clear names, proper validation, and serve specific purposes in your ROT13 API architecture.