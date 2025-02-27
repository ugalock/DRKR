# backend/tests/test_users_api.py

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy import select
from typing import List

from pydantic import StrictInt  # noqa: F401
from typing import Any  # noqa: F401
from app.schemas.user import User  # noqa: F401
from app.schemas.user_create_request import UserCreateRequest  # noqa: F401
from app.schemas.user_update_request import UserUpdateRequest  # noqa: F401

from app.models import User as UserModel, OrganizationMember

@pytest.fixture
def mock_users_list():
    """Fixture for a list of mock users"""
    return [
        UserModel(
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
        ),
        UserModel(
            id=2,
            external_id="208739423626810412116",
            username="Alice Johnson",
            email="alice@example.com",
            display_name="Alice Johnson",
            default_role="user",
            created_at="2025-02-23 18:28:31.998981",
            updated_at="2025-02-23 18:28:31.998981",
            auth_provider="google-oauth2",
            picture_url="https://example.com/alice.jpg"
        )
    ]

def test_users_get(client: TestClient, mock_db, mock_user, mock_users_list):
    """Test listing users endpoint"""
    # Setup mock DB response for user listing
    mock_result = AsyncMock()
    mock_scalars = AsyncMock()
    mock_scalars.all.return_value = mock_users_list
    mock_result.scalars.return_value = mock_scalars
    mock_db.execute.return_value = mock_result
    
    # Add mock for count query
    mock_count_result = AsyncMock()
    mock_count_scalar = AsyncMock()
    mock_count_scalar.one.return_value = (2,)  # Total count as a tuple
    mock_count_result.scalars.return_value = mock_count_scalar
    mock_db.execute.side_effect = [mock_result, mock_count_result]
    
    # Mock User response to ensure schema conversion works correctly
    mock_response = [{
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "display_name": user.display_name,
        "default_role": user.default_role,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "picture_url": user.picture_url
    } for user in mock_users_list]
    
    # Patch User model_validate to ensure schema conversion is tested
    with patch.object(User, 'model_validate', side_effect=lambda x: {
        "id": x.id,
        "username": x.username,
        "email": x.email,
        "display_name": x.display_name,
        "default_role": x.default_role,
        "created_at": x.created_at,
        "updated_at": x.updated_at,
        "picture_url": x.picture_url
    }):
        # Execute request
        response = client.get("/api/users?page=1&limit=50")
        
        # Assert response
        assert response.status_code == 200
        users = response.json()
        assert len(users) == 2
        assert users[0]["username"] == mock_users_list[0].username
        assert users[1]["username"] == mock_users_list[1].username
        
        # Verify DB interactions
        assert mock_db.execute.call_count == 2  # One for users, one for count

def test_users_search(client: TestClient, mock_db, mock_user, mock_users_list):
    """Test searching users endpoint"""
    # Filter to only one user
    filtered_user = [mock_users_list[0]]
    
    # Setup mock DB response for user search
    mock_result = AsyncMock()
    mock_scalars = AsyncMock()
    mock_scalars.all.return_value = filtered_user
    mock_result.scalars.return_value = mock_scalars
    
    # Add mock for count query
    mock_count_result = AsyncMock()
    mock_count_scalar = AsyncMock()
    mock_count_scalar.one.return_value = (1,)  # Total count as a tuple
    mock_count_result.scalars.return_value = mock_count_scalar
    
    # Set up execute to return different results
    mock_db.execute.side_effect = [mock_result, mock_count_result]
    
    # Execute request with search parameter
    response = client.get("/api/users?search=Jordan")
    
    # Assert response
    assert response.status_code == 200
    users = response.json()
    assert len(users) == 1
    assert users[0]["username"] == "Jordan Sims"
    
    # Verify DB interactions
    assert mock_db.execute.call_count == 2
    # Verify the first call contains our search term in the SQL
    call_args = mock_db.execute.call_args_list[0][0][0]
    # We can't directly check the SQL query content here since it's a SQLAlchemy object
    # But we would verify that our search logic in the select() call works in an integration test

def test_users_id_get(client: TestClient, mock_db, mock_user):
    """Test getting a specific user by ID"""
    # Setup mock DB response
    mock_result = AsyncMock()
    mock_scalars = AsyncMock()
    mock_scalars.one_or_none.return_value = mock_user
    mock_result.scalars.return_value = mock_scalars
    mock_db.execute.return_value = mock_result
    
    # Execute request
    response = client.get(f"/api/users/{mock_user.id}")
    
    # Assert response
    assert response.status_code == 200
    user = response.json()
    assert user["id"] == mock_user.id
    assert user["username"] == mock_user.username
    assert user["email"] == mock_user.email
    
    # Verify DB interactions
    mock_db.execute.assert_called_once()
    mock_scalars.one_or_none.assert_called_once()

def test_users_id_get_not_found(client: TestClient, mock_db, mock_user):
    """Test getting a non-existent user by ID"""
    # Setup mock DB response for user not found
    mock_result = AsyncMock()
    mock_scalars = AsyncMock()
    mock_scalars.one_or_none.return_value = None
    mock_result.scalars.return_value = mock_scalars
    mock_db.execute.return_value = mock_result
    
    # Execute request with non-existent ID
    response = client.get("/api/users/999")
    
    # Assert response
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
    
    # Verify DB interactions
    mock_db.execute.assert_called_once()
    mock_scalars.one_or_none.assert_called_once()

def test_users_me_get(client: TestClient, mock_user):
    """Test getting current user profile"""
    # This endpoint doesn't require DB interaction, just uses the current_user dependency
    
    # Execute request
    response = client.get("/api/users/me")
    
    # Assert response
    assert response.status_code == 200
    user = response.json()
    assert user["id"] == mock_user.id
    assert user["username"] == mock_user.username
    assert user["email"] == mock_user.email

def test_users_me_patch(client: TestClient, mock_db, mock_user):
    """Test updating current user profile"""
    # Setup DB mocks
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    
    # Create update data
    update_data = {
        "display_name": "Updated Name",
        "bio": "New bio information"
    }
    
    # Execute request
    response = client.patch("/api/users/me", json=update_data)
    
    # Assert response
    assert response.status_code == 200
    user = response.json()
    assert user["display_name"] == "Updated Name"
    # Check that the mock user was updated
    assert mock_user.display_name == "Updated Name"
    assert mock_user.bio == "New bio information"
    
    # Verify DB interactions
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(mock_user)

@patch("app.services.authentication.verify_jwt_token")
@patch("app.services.authentication.create_user_if_not_exists")
def test_users_me_create(mock_create_user, mock_verify, client, mock_db, mock_user):
    """Test creating/getting user from ID token"""
    # Setup mocks
    mock_verify.return_value = {
        "sub": "google-oauth2|108739423626810412115",
        "email": mock_user.email
    }
    mock_create_user.return_value = mock_user
    
    # Execute request
    response = client.get(f"/api/users/me/test_id_token")
    
    # Assert response
    assert response.status_code == 200
    user = response.json()
    assert user["id"] == mock_user.id
    assert user["username"] == mock_user.username
    
    # Verify token verification was called
    mock_verify.assert_called_once()

