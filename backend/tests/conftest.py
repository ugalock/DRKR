import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app as application
from app.db import get_db
from app.models import User, ApiKey
from app.services.authentication import get_current_user, verify_api_key

# Mock user for authentication
@pytest.fixture
def mock_user():
    return User(
        id=1,
        external_id="108739423626810412115",
        username="Jordan Sims",
        email="ugalock@gmail.com",
        display_name="Jordan Sims",
        default_role="user",
        created_at="2025-02-23 18:28:31.998981",
        updated_at="2025-02-23 18:28:31.998981",
        auth_provider="google-oauth2",
        picture_url="https://lh3.googleusercontent.com/a/ACg8ocKskozhgaRFBR_bY0VijkwS9z22e7qtB3bLiDJVo3uFOts_dA=s96-c"
    )

# Mock AsyncSession for DB operations
@pytest.fixture
def mock_db():
    """Enhanced mock db that properly handles async methods"""
    db = AsyncMock(spec=AsyncSession)
    
    # Make common methods return awaitable coroutines with proper attributes for assertion
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.add = AsyncMock()
    db.scalar = AsyncMock(return_value=0)  # Default count for queries
    db.execute = AsyncMock()
    
    return db

# Override app dependencies
@pytest.fixture
def app(mock_user, mock_db):
    """App fixture with proper async dependency overrides"""
    
    async def override_get_db():
        yield mock_db

    async def override_get_current_user():
        return mock_user
    
    async def override_verify_api_key():
        return mock_user
    
    # Override the dependencies
    application.dependency_overrides[get_db] = override_get_db
    application.dependency_overrides[get_current_user] = override_get_current_user
    application.dependency_overrides[verify_api_key] = override_verify_api_key

    yield application
    
    # Clean up
    application.dependency_overrides = {}

@pytest.fixture
def client(app) -> TestClient:
    """Test client fixture"""
    return TestClient(app)
