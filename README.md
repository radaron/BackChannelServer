# BackChannel Server

A FastAPI application with JWT authentication, SQLAlchemy ORM, and Docker support.

## Features

- 🚀 FastAPI web framework
- 🔐 Cookie-based authentication with master password
- 🍪 Secure session management
- 📦 Poetry dependency management
- 🐳 Docker containerization
- 📊 API documentation with Swagger UI

## Project Structure

```
BackChannelServer/
├── app/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py          # App configuration
│   │   ├── database.py        # Database setup
│   │   └── security.py        # JWT & password utilities
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py           # SQLAlchemy models
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py           # Authentication endpoints
│   │   └── client.py         # Client endpoints
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user.py           # Pydantic schemas
│   ├── __init__.py
│   └── main.py               # FastAPI app
├── Dockerfile
├── .dockerignore
├── .gitignore
└── pyproject.toml
```

## Quick Start

### Using Poetry (Recommended)

1. **Install dependencies:**
   ```bash
   poetry install
   ```

2. **Run the application:**
   ```bash
   poetry run python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Access the API:**
   - API Documentation: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Using Docker

1. **Build the image:**
   ```bash
   docker build -t backchannel-server .
   ```

2. **Run the container:**
   ```bash
   docker run -p 8000:8000 backchannel-server
   ```

## Authentication

The application uses a simple master password for authentication:
- **Master Password:** `admin123` (configurable via environment)

### Password Hashing

For enhanced security, you can use hashed passwords instead of plain text:

#### Generate Password Hash

**Option 1: Using Poetry scripts (recommended)**
```bash
# Hash any password
poetry run hash-password admin123

# Hash the current master password from config
poetry run hash-master-password
```

**Option 1b: Using Make commands**
```bash
# Hash any password
make hash-password PASSWORD=admin123

# Hash the current master password from config
make hash-master
```

**Option 2: Using the CLI script directly**
```bash
python hash_password.py admin123
```

**Option 3: Using the API endpoint (requires authentication)**
```bash
# First login to get authenticated
curl -c cookies.txt -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"password": "admin123"}'

# Then hash a password
curl -b cookies.txt -X POST "http://localhost:8000/api/v1/auth/hash-password" \
     -H "Content-Type: application/json" \
     -d '{"password": "mynewpassword"}'
```

**Option 4: Using Python directly**
```python
from app.core.security import hash_password
hashed = hash_password("admin123")
print(f"MASTER_PASSWORD_HASH={hashed}")
```

#### Using Hashed Passwords

Set the hashed password in your `.env` file:
```bash
MASTER_PASSWORD_HASH=$2b$12$example.hash.here
# When MASTER_PASSWORD_HASH is set, MASTER_PASSWORD is ignored for authentication
```

### API Endpoints

#### Authentication (`/api/v1/auth`)

- `POST /api/v1/auth/login` - Login with master password (sets session cookie)
- `POST /api/v1/auth/logout` - Logout and clear session cookie
- `GET /api/v1/auth/me` - Get current session info
- `GET /api/v1/auth/status` - Check authentication status
- `POST /api/v1/auth/hash-password` - Hash a password (requires authentication)

#### Client (`/api/v1/client`)

- `GET /api/v1/client/profile` - Get session profile
- `GET /api/v1/client/dashboard` - Get dashboard data
- `GET /api/v1/client/stats` - Get session statistics
- `GET /api/v1/client/protected` - Example protected endpoint

### Example Usage

1. **Login with master password:**
   ```bash
   curl -c cookies.txt -X POST "http://localhost:8000/api/v1/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"password": "admin123"}'
   ```

2. **Access protected endpoint:**
   ```bash
   curl -b cookies.txt -X GET "http://localhost:8000/api/v1/client/profile"
   ```

3. **Check authentication status:**
   ```bash
   curl -b cookies.txt -X GET "http://localhost:8000/api/v1/auth/status"
   ```

4. **Logout:**
   ```bash
   curl -b cookies.txt -c cookies.txt -X POST "http://localhost:8000/api/v1/auth/logout"
   ```

## Configuration

Configuration can be customized via environment variables or the `.env` file:

- `SECRET_KEY` - Session secret key (change in production!)
- `MASTER_PASSWORD` - Master password for authentication (default: admin123)
- `MASTER_PASSWORD_HASH` - Hashed master password (preferred over plain text)
- `SESSION_EXPIRE_MINUTES` - Session expiration time (default: 60 minutes)
- `COOKIE_NAME` - Session cookie name (default: backchannel_session)

## Development

### Install development dependencies:
```bash
poetry install --with dev
```

### Code formatting:
```bash
poetry run black app/
poetry run isort app/
```

### Type checking:
```bash
poetry run mypy app/
```

### Available Make Commands:
```bash
make install           # Install dependencies
make run              # Run FastAPI server in development mode
make hash-password PASSWORD=yourpass  # Hash any password
make hash-master      # Hash current master password from config
make format           # Format code with isort and black
make up               # Run with Docker Compose
```

### Run tests:
```bash
poetry run pytest
```

## Docker Commands

```bash
# Build image
docker build -t backchannel-server .

# Run container
docker run -p 8000:8000 backchannel-server

# Run with environment variables
docker run -p 8000:8000 -e SECRET_KEY=your-secret-key -e MASTER_PASSWORD=your-password backchannel-server

# Run in background
docker run -d -p 8000:8000 --name backchannel backchannel-server
```

## License

This project is open source and available under the [MIT License](LICENSE).