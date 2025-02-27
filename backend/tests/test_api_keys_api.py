import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta, timezone
from app.models import ApiKey, User
from sqlalchemy.ext.asyncio import AsyncSession
import secrets

@pytest.fixture
def mock_api_key():
    """Create a mock API key for testing"""
    return ApiKey(
        id=1,
        token="test_api_key_123",  # Shortened for clarity
        name="Test API Key",
        user_id=1,
        is_active=True,
        expires_at=datetime.now(timezone.utc) + timedelta(days=30),
        created_at=datetime.now(timezone.utc)
    )

def test_create_api_key(client: TestClient, mock_db, mock_user):
    """Test the create API key endpoint"""
    # Mock datetime.now to return a consistent value
    mock_now = datetime(2023, 1, 1, tzinfo=timezone.utc)
    mock_future = mock_now + timedelta(days=30)
    
    # Create test data
    api_key_data = {
        "name": "Test API Key",
        "expires_in_days": 30
    }

    # Mock the API key token
    token = "test_api_key_token"
    
    # Setup the mock ApiKey that will be returned
    mock_api_key = MagicMock()
    mock_api_key.id = 1
    mock_api_key.token = token
    mock_api_key.name = "Test API Key"
    mock_api_key.user_id = mock_user.id
    mock_api_key.organization_id = None
    mock_api_key.is_active = True
    mock_api_key.created_at = mock_now
    mock_api_key.expires_at = mock_future

    # Setup db mocks
    mock_db.add = AsyncMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    
    # Set up the refresh side effect to set created_at and expires_at
    def refresh_side_effect(obj):
        obj.id = 1
        obj.created_at = mock_now
        obj.expires_at = mock_future
        return None
    
    mock_db.refresh.side_effect = refresh_side_effect
    
    # Prepare the expected response data
    expected_response = {
        "token": token,
        "name": "Test API Key",
        "user_id": mock_user.id,
        "organization_id": None,
        "is_active": True,
        "created_at": mock_now.isoformat(),
        "expires_at": mock_future.isoformat()
    }
    
    # Mock the ApiKey class to return our mock
    with patch("app.routers.api_keys.ApiKey", return_value=mock_api_key), \
         patch("app.routers.api_keys.secrets.token_urlsafe", return_value=token), \
         patch("app.routers.api_keys.datetime") as mock_datetime:
        
        # Configure mock datetime
        mock_datetime.utcnow.return_value = mock_now
        mock_datetime.UTC = timezone.utc
        
        # Execute request
        response = client.post("/api/api-keys", json=api_key_data)
        
        # Validate the response
        assert response.status_code == 200
        assert response.json() == expected_response
        
        # Verify the mocks were called correctly
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

def test_list_api_keys(client: TestClient, mock_db, mock_user, mock_api_key):
    """Test the list API keys endpoint"""
    # Setup mock result that properly handles async/await
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_api_key]
    
    # Configure the mock db execute to handle the async call
    mock_db.execute = AsyncMock(return_value=mock_result)
    
    # Mock ApiKeyResponse model_validate to return a valid response
    mock_response = {
        "id": 1,
        "name": "Test API Key",
        "token": "test_api_key_123",
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    }
    
    # Patch the model_validate method
    with patch("app.routers.api_keys.ApiKeyResponse.model_validate", return_value=mock_response):
        # Execute request
        response = client.get("/api/api-keys")
        
        # Assertions
        assert response.status_code == 200
        assert len(response.json()) == 1
        api_key_data = response.json()[0]
        assert api_key_data["name"] == "Test API Key"
        
        # Verify db.execute was called
        assert mock_db.execute.called

def test_revoke_api_key(client: TestClient, mock_db, mock_user, mock_api_key):
    """Test the revoke API key endpoint"""
    # Setup mock result that properly handles async/await
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_api_key
    
    # Configure the mock db execute to handle the async call
    mock_db.execute = AsyncMock(return_value=mock_result)
    
    # Execute request
    response = client.delete(f"/api/api-keys/1")
    
    # Assertions
    assert response.status_code == 200
    assert "message" in response.json()
    assert "revoked" in response.json()["message"].lower()
    
    # Verify db operations were called
    assert mock_db.execute.called
    assert mock_db.commit.called

def test_revoke_api_key_not_found(client: TestClient, mock_db, mock_user):
    """Test the revoke API key endpoint when key is not found"""
    # Setup mock result that properly handles async/await
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    
    # Configure the mock db execute to handle the async call
    mock_db.execute = AsyncMock(return_value=mock_result)
    
    # Execute request
    response = client.delete("/api/api-keys/999")  # Non-existent key
    
    # Assertions
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
    
    # Verify db.execute was called but not commit
    assert mock_db.execute.called
    assert not hasattr(mock_db.commit, 'called') or not mock_db.commit.called 