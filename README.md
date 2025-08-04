##  ROT13 API Project 

This is a simple web API that built to encode text using the ROT13 cipher. It uses Python with FastAPI and includes user authentication.

## Core Features

- **ROT13 Cipher Encoding**: Simple letter substitution cipher that shifts each letter 13 positions in the alphabet
- **JWT Authentication**: Secure token-based authentication system with 30-minute token expiration
- **Rate Limiting**: Built-in protection against API abuse with request throttling
- **CORS Support**: Cross-origin resource sharing enabled for frontend integration
- **RESTful API**: Clean, well-documented endpoints following REST principles
- **Input Validation**: Robust data validation using Pydantic schemas
- **Health Monitoring**: Built-in health check endpoint for system monitoring

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

## Installation & Setup

### Option 1: Local Installation

```bash
pip install -r requirements.txt
python main.py
```

The server will run on http://localhost:8000

### Option 2: Docker (Recommended)

#### Using Docker Compose (Easiest)
```bash
# Clone the repository
git clone <repository-url>
cd rot13-fastapi

# Build and run with Docker Compose
docker-compose up --build
```

#### Using Docker directly
```bash
# Build the Docker image
docker build -t rot13-api .

# Run the container
docker run -p 8000:8000 rot13-api
```

The server will be available at http://localhost:8000

### Option 3: Development with Docker
```bash
# For development with auto-reload
docker-compose up --build

# To rebuild after changes
docker-compose down
docker-compose up --build
```

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

Demo users are available for testing the authentication system. Check the [`users.py`](users.py) file for available test accounts.

## The ROT13 algorithm

The ROT13 implementation handles uppercase letters and spaces, with proper validation to ensure correct input format. The algorithm shifts each letter 13 positions in the alphabet and wraps around when necessary.

## Dependencies

The main libraries I used:
- **FastAPI** - The web framework
- **Uvicorn** - Server to run the app
- **Pydantic** - Data validation
- **python-jose** - JWT token handling
- **slowapi** - Rate limiting
- **python-multipart** - For handling form data in login



## GitHub Repository

This project is hosted on GitHub. You can:

- **Clone the repository**: `git clone <repository-url>`
- **Fork the project**: Click the "Fork" button on GitHub to create your own copy
- **Submit issues**: Report bugs or request features using GitHub Issues
- **Contribute**: Submit pull requests with improvements or fixes

### Repository Structure
```
rot13-fastapi/
├── main.py              # Main FastAPI application
├── auth_endpoints.py    # Authentication endpoints
├── oauth2.py           # JWT token handling
├── utils.py            # ROT13 cipher implementation
├── users.py            # User management
├── models.py           # Data models
├── schemas.py          # Pydantic schemas
├── config.py           # Configuration settings
├── rate_limiter.py     # Rate limiting functionality
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker container configuration
├── docker-compose.yaml # Docker Compose setup
└── README.md          # This file
```

## Docker Information

This project includes Docker support for easy deployment and development.

### Docker Files
- **[`Dockerfile`](Dockerfile)**: Defines the container image using Python 3.11
- **[`docker-compose.yaml`](docker-compose.yaml)**: Orchestrates the application container

### Docker Features
- **Lightweight**: Based on Python 3.11 official image
- **Port Mapping**: Exposes port 8000 for API access
- **Easy Deployment**: Single command deployment with Docker Compose
- **Development Ready**: Supports development workflows

### Docker Commands Reference
```bash
# Build the image
docker build -t rot13-api .

# Run container
docker run -p 8000:8000 rot13-api

# Using Docker Compose
docker-compose up --build    # Build and start
docker-compose down          # Stop and remove containers
docker-compose logs          # View logs
```

### Production Deployment
For production deployment, consider:
- Using environment variables for configuration
- Setting up proper logging
- Implementing health checks
- Using a reverse proxy (nginx)
- Setting up SSL/TLS certificates

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is open source and available under the [MIT License](LICENSE).
