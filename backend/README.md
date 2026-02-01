# Receipts Backend

A proof-first short-form social platform API built with FastAPI.

## Quick Start

### Prerequisites

- Python 3.11+
- pip

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Copy environment file
cp .env.example .env

# Run development server
python -m uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── api/           # API endpoints (thin layer)
│   │   ├── health.py
│   │   └── v1/        # Version 1 API
│   │       ├── auth.py
│   │       ├── users.py
│   │       ├── receipts.py
│   │       ├── evidence.py
│   │       ├── feed.py
│   │       ├── topics.py
│   │       ├── reactions.py
│   │       ├── moderation.py
│   │       ├── exports.py
│   │       └── uploads.py
│   ├── core/          # Core utilities
│   │   ├── config.py      # Environment settings
│   │   ├── security.py    # Auth primitives
│   │   ├── dependencies.py # DI hooks
│   │   ├── logging.py     # Structured logging
│   │   └── rate_limit.py  # Rate limiting
│   ├── db/            # Database layer
│   │   ├── session.py     # Connection management
│   │   └── repositories/  # Data access
│   ├── models/        # Data models
│   │   ├── db/            # SQLAlchemy ORM models
│   │   ├── schemas/       # Pydantic request/response
│   │   └── enums.py       # Enum types
│   ├── services/      # Business logic (ALL logic here)
│   └── main.py        # Application entry point
├── tests/             # Test suite
├── scripts/           # Utility scripts
├── pyproject.toml     # Dependencies
└── .env.example       # Environment template
```

## Architecture Rules

1. **All business logic lives in `services/`**
2. API routes are thin - they delegate to services
3. Services are the only layer that touches repositories
4. Repositories are the only layer that touches the database

## Key Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user

### Receipts
- `POST /api/v1/receipts` - Create receipt
- `GET /api/v1/receipts/{id}` - Get receipt
- `DELETE /api/v1/receipts/{id}` - Delete receipt
- `POST /api/v1/receipts/{id}/fork` - Fork/counter receipt
- `GET /api/v1/receipts/{id}/chain` - Get receipt chain

### Feed
- `GET /api/v1/feed` - Home feed
- `GET /api/v1/feed/trending` - Trending chains
- `GET /api/v1/feed/topic/{slug}` - Topic feed

### Exports
- `POST /api/v1/receipts/{id}/export` - Generate receipt card
- `GET /api/v1/exports/{id}` - Get export status

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/api/test_auth.py
```

## Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `DATABASE_URL` - Database connection string
- `SECRET_KEY` - JWT signing key (generate with `openssl rand -hex 32`)
- `CORS_ORIGINS` - Allowed frontend origins
- `STORAGE_BACKEND` - `local` or `s3`

## License

Proprietary - ALÁON AGI LLC
