from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from schemas import Token
from users import authenticate_user
from oauth2 import create_access_token
from rate_limiter import limiter

# router auth endpoints

router = APIRouter()

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def user_login(request: Request, credentials: OAuth2PasswordRequestForm = Depends()):
    """User login - returns JWT token"""
    # Check if user exists and password is correct
    user = authenticate_user(credentials.username, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    token = create_access_token(data={"username": user["username"]})
    
    return {"access_token": token, "token_type": "bearer"}