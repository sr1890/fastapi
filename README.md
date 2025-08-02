##  ROT13 API Project 

This is a simple web API that built to encode text using the ROT13 cipher. It uses Python with FastAPI and includes user authentication.

## What does this project do?

ROT13 is a basic cipher where you replace each letter with the letter 13 positions ahead in the alphabet. So A becomes N, B becomes O, and so on. It's like a simple code that you can easily decode by applying ROT13 again.

For example:
- "HELLO" becomes "URYYB"

## How its Build 

Used FastAPI. The project has several parts:

- **Main API** (`main.py`) - This is where all the web endpoints are defined
- **Authentication** (`auth_endpoints.py` and `oauth2.py`) - Handles user login and JWT tokens
- **ROT13 Logic** (`utils.py`) - The actual cipher implementation
- **User Storage** (`users.py`) - Simple demo users for testing
- **Configuration** (`config.py`) - Settings for JWT tokens
- **Rate Limiting** (`rate_limiter.py`) - Prevents people from spamming the API

##  Security features

I added JWT (JSON Web Token) authentication because I wanted to make it secure. Users have to log in first to get a token, then use that token for all other requests. The tokens expire after 30 minutes for security.

I also added rate limiting so people can't make too many requests too quickly and overwhelm the server.

I also added CORS (Cross-Origin Resource Sharing) middleware to allow the API to be accessed from web browsers running on different domains. This is essential for frontend applications that need to communicate with the API.

## How to use it 

## Starting the server 

```
pip install -r requirements.txt
python main.py
```

The server will run on http://localhost:8000

### Getting a token
First, you need to log in:
```bash
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testuser123"
```

This gives you back a token that looks like a long random string.

### Encoding text
Then you can encode text by sending it with your token:
```bash
curl -X POST "http://localhost:8000/api/rot13" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"text": "HELLO WORLD"}'
```

You'll get back: `{"result": "URYYB JBEYQ", "user": "testuser"}`

## Available endpoints

- **POST /login** - Log in with username/password to get a token
- **POST /api/rot13** - Encode text (requires token)
- **GET /api/user-info** - Get your user information (requires token)
- **GET /health** - Check if the server is running
- **GET /** - Basic API information

## Test users

I included two demo users you can use:
- Username: `testuser`, Password: `testuser123`
- Username: `admin`, Password: `admin123`

## The ROT13 algorithm

Here's how I implemented the ROT13 encoding:

```python
def encodeRot13(input_text):
    output = ""
    for letter in input_text:
        if letter == ' ':
            output += ' '  # Keep spaces as they are
        else:
            pos = ord(letter) - ord('A')  # Get position (A=0, B=1, etc.)
            new_pos = (pos + 13) % 26     # Add 13 and wrap around
            new_letter = chr(new_pos + ord('A'))  # Convert back to letter
            output += new_letter
    return output
```

It only works with uppercase letters and spaces. I added validation to make sure people only send the right kind of text.

## Dependencies

The main libraries I used:
- **FastAPI** - The web framework
- **Uvicorn** - Server to run the app
- **Pydantic** - Data validation
- **python-jose** - JWT token handling
- **slowapi** - Rate limiting
- **python-multipart** - For handling form data in login

