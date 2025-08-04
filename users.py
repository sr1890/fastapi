USERS = {
    "testuser": {
        "id": 1,
        "username": "testuser",
        "password": "testuser123"
    },
    "admin": {
        "id": 2,
        "username": "admin", 
        "password": "admin123"
    }
}

def get_user(username: str):
    """Get user by username"""
    return USERS.get(username)

def authenticate_user(username: str, password: str):
    """Check if username and password are correct"""
    user = get_user(username)
    if user and user["password"] == password:
        return user
    return None