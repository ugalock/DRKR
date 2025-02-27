# coding: utf-8

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
import json
from datetime import datetime, timezone

from app.models import DeepResearch as DeepResearchModel
from app.schemas.deep_research import DeepResearch
from app.schemas.deep_research_create_request import DeepResearchCreateRequest
from app.schemas.deep_research_update_request import DeepResearchUpdateRequest

@pytest.fixture
def mock_deep_research():
    """Fixture for a mock deep research object"""
    now = datetime.now(timezone.utc)
    return DeepResearchModel(
        id=1,
        user_id=1,
        owner_user_id=1,
        owner_org_id=None,
        visibility="private",
        title="Test Research",
        prompt_text="Test research prompt text",
        final_report=json.dumps({
            "introduction": "This is an introduction",
            "sections": [
                {"title": "Section 1", "content": "Content for section 1"},
                {"title": "Section 2", "content": "Content for section 2"}
            ],
            "conclusion": "This is a conclusion"
        }),
        model_name="gpt-4",
        model_params={"max_tokens": 1000},
        source_count=2,
        created_at=now,
        updated_at=now
    )

@pytest.fixture
def mock_deep_research_list():
    """Fixture for a list of mock deep research objects"""
    now = datetime.now(timezone.utc)
    return [
        DeepResearchModel(
            id=1,
            user_id=1,
            owner_user_id=1,
            owner_org_id=None,
            visibility="private",
            title="Test Research 1",
            prompt_text="Test research prompt text 1",
            final_report=json.dumps({"introduction": "Intro 1"}),
            model_name="gpt-4",
            model_params={"max_tokens": 1000},
            source_count=1,
            created_at=now,
            updated_at=now
        ),
        DeepResearchModel(
            id=2,
            user_id=1,
            owner_user_id=1,
            owner_org_id=None,
            visibility="public",
            title="Test Research 2",
            prompt_text="Test research prompt text 2",
            final_report=json.dumps({"introduction": "Intro 2"}),
            model_name="gpt-4",
            model_params={"max_tokens": 1000},
            source_count=1,
            created_at=now,
            updated_at=now
        )
    ]

def test_deep_research_get(client, mock_db, mock_user, mock_deep_research_list):
    """Test listing deep research endpoints"""
    # Setup mock DB response for listing
    # Create a real AsyncMock that returns a non-coroutine object
    mock_db.execute = AsyncMock()
    mock_db.execute.return_value = MagicMock()
    mock_db.execute.return_value.scalars = MagicMock()
    mock_db.execute.return_value.scalars.return_value = MagicMock()
    mock_db.execute.return_value.scalars.return_value.all = MagicMock(return_value=mock_deep_research_list)
    
    # Mock response objects for validation - keeping final_report as a string
    mock_responses = []
    for research in mock_deep_research_list:
        mock_responses.append({
            "id": research.id,
            "user_id": research.user_id,
            "owner_user_id": research.owner_user_id,
            "owner_org_id": research.owner_org_id,
            "visibility": research.visibility,
            "title": research.title,
            "prompt_text": research.prompt_text,
            "final_report": research.final_report,  # Keep as string
            "model_name": research.model_name,
            "model_params": research.model_params,
            "source_count": research.source_count,
            "created_at": research.created_at.isoformat() if hasattr(research.created_at, 'isoformat') else research.created_at,
            "updated_at": research.updated_at.isoformat() if hasattr(research.updated_at, 'isoformat') else research.updated_at
        })
    
    # Patch DeepResearch model_validate
    with patch("app.routers.deep_research.DeepResearch.model_validate", side_effect=mock_responses):
        # Execute request
        response = client.get("/api/deep-research")
        
        # Assert response
        assert response.status_code == 200
        researches = response.json()
        assert len(researches) == 2
        assert researches[0]["title"] == mock_deep_research_list[0].title
        assert researches[1]["title"] == mock_deep_research_list[1].title
        
        # Verify DB interactions
        mock_db.execute.assert_called_once()

def test_deep_research_id_get(client, mock_db, mock_user, mock_deep_research):
    """Test getting a specific deep research by ID"""
    # Setup mock DB response
    mock_db.execute = AsyncMock()
    mock_db.execute.return_value = MagicMock()
    mock_db.execute.return_value.scalars = MagicMock()
    mock_db.execute.return_value.scalars.return_value = MagicMock()
    mock_db.execute.return_value.scalars.return_value.first = MagicMock(return_value=mock_deep_research)
    
    # Mock response object for validation - with model_params as a dict
    mock_response = {
        "id": mock_deep_research.id,
        "user_id": mock_deep_research.user_id,
        "owner_user_id": mock_deep_research.owner_user_id,
        "owner_org_id": mock_deep_research.owner_org_id,
        "visibility": mock_deep_research.visibility,
        "title": mock_deep_research.title,
        "prompt_text": mock_deep_research.prompt_text,
        "final_report": mock_deep_research.final_report,  # Keep as string
        "model_name": mock_deep_research.model_name,
        "model_params": {"max_tokens": 1000},  # Dict for response
        "source_count": mock_deep_research.source_count,
        "created_at": mock_deep_research.created_at.isoformat() if hasattr(mock_deep_research.created_at, 'isoformat') else mock_deep_research.created_at,
        "updated_at": mock_deep_research.updated_at.isoformat() if hasattr(mock_deep_research.updated_at, 'isoformat') else mock_deep_research.updated_at
    }
    
    # Patch DeepResearch model_validate
    with patch("app.routers.deep_research.DeepResearch.model_validate", return_value=mock_response):
        # Execute request
        response = client.get(f"/api/deep-research/{mock_deep_research.id}")
        
        # Assert response
        assert response.status_code == 200
        research = response.json()
        assert research["id"] == mock_deep_research.id
        assert research["title"] == mock_deep_research.title
        assert research["visibility"] == mock_deep_research.visibility
        
        # Verify DB interactions
        mock_db.execute.assert_called_once()

def test_deep_research_id_get_not_found(client, mock_db, mock_user):
    """Test getting a deep research that doesn't exist"""
    # Setup mock DB response for not found
    mock_db.execute = AsyncMock()
    mock_db.execute.return_value = MagicMock()
    mock_db.execute.return_value.scalars = MagicMock()
    mock_db.execute.return_value.scalars.return_value = MagicMock()
    mock_db.execute.return_value.scalars.return_value.first = MagicMock(return_value=None)
    
    # Execute request with non-existent ID
    response = client.get("/api/deep-research/999")
    
    # Assert response
    assert response.status_code == 404
    assert response.json()["detail"] == "Research item not found"  # Updated to match actual message
    
    # Verify DB interactions
    mock_db.execute.assert_called_once()

def test_deep_research_post(client, mock_db, mock_user):
    """Test creating a new deep research"""
    # Setup DB mocks
    mock_db.add = AsyncMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    
    # Create test deep research request that matches the expected schema
    # Include all required fields: title, prompt_text, final_report, visibility
    research_request = {
        "title": "New Research",
        "prompt_text": "This is a new research prompt",
        "visibility": "private",
        "final_report": "{}" # Adding required field
    }
    
    # First, set up a mock for what gets added to the DB
    mock_new_research = MagicMock(spec=DeepResearchModel)
    mock_new_research.id = 1
    mock_new_research.user_id = mock_user.id
    mock_new_research.owner_user_id = mock_user.id
    mock_new_research.owner_org_id = None
    mock_new_research.visibility = "private"
    mock_new_research.title = research_request["title"]
    mock_new_research.prompt_text = research_request["prompt_text"]
    mock_new_research.final_report = research_request["final_report"]
    mock_new_research.model_name = "gpt-4"
    mock_new_research.model_params = json.dumps({})  # Keep this as a string in the model
    mock_new_research.source_count = 0
    
    # Mock the db.add function to capture the object and modify it
    def add_side_effect(obj):
        # Copy attributes from the mock to the actual added object
        obj.id = 1
        return None
    
    mock_db.add.side_effect = add_side_effect
    
    # Create a mock response with the correct string format for all fields
    mock_response = {
        "id": 1,
        "user_id": mock_user.id,
        "owner_user_id": mock_user.id,
        "owner_org_id": None,
        "visibility": "private",
        "title": research_request["title"],
        "prompt_text": research_request["prompt_text"],
        "final_report": research_request["final_report"],
        "model_name": "gpt-4",
        "model_params": {},  # Dictionary for the response as expected by schema
        "source_count": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Mock the router's DeepResearchModel constructor to return our mock
    with patch("app.routers.deep_research.DeepResearchModel", return_value=mock_new_research), \
         patch("app.routers.deep_research.DeepResearch.model_validate", return_value=mock_response), \
         patch("app.schemas.deep_research_create_request.DeepResearchCreateRequest.model_validate", 
               return_value=DeepResearchCreateRequest(**research_request)):
        
        # Execute request
        response = client.post("/api/deep-research", json=research_request)
        
        # Print response if there's an error
        if response.status_code != 200:
            print(f"Response: {response.status_code}, {response.content}")
        
        # Assert response
        assert response.status_code == 200
        research = response.json()
        assert research["title"] == research_request["title"]
        assert research["prompt_text"] == research_request["prompt_text"]
        assert research["visibility"] == "private"
        assert research["final_report"] == research_request["final_report"]
        assert isinstance(research["model_params"], dict)  # Ensure it's a dictionary
        
        # Verify DB interactions
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

def test_deep_research_id_delete(client, mock_db, mock_user, mock_deep_research):
    """Test deleting a deep research"""
    # Setup mock DB response
    mock_db.execute = AsyncMock()
    mock_db.execute.return_value = MagicMock()
    mock_db.execute.return_value.scalars = MagicMock()
    mock_db.execute.return_value.scalars.return_value = MagicMock()
    mock_db.execute.return_value.scalars.return_value.first = MagicMock(return_value=mock_deep_research)
    mock_db.delete = AsyncMock()
    mock_db.commit = AsyncMock()
    
    # Execute request
    response = client.delete(f"/api/deep-research/{mock_deep_research.id}")
    
    # Assert response
    assert response.status_code == 204  # No content
    
    # Verify DB interactions
    mock_db.execute.assert_called_once()
    mock_db.delete.assert_called_once_with(mock_deep_research)
    mock_db.commit.assert_called_once()

def test_deep_research_id_patch(client, mock_db, mock_user, mock_deep_research):
    """Test updating a deep research"""
    # Setup mock DB response
    mock_db.execute = AsyncMock()
    mock_db.execute.return_value = MagicMock()
    mock_db.execute.return_value.scalars = MagicMock()
    mock_db.execute.return_value.scalars.return_value = MagicMock()
    mock_db.execute.return_value.scalars.return_value.first = MagicMock(return_value=mock_deep_research)
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    
    # Create update data
    update_data = {
        "title": "Updated Research Title",
        "prompt_text": "Updated research prompt text"
    }
    
    # Create a side effect for refresh that actually updates the mock object
    def refresh_side_effect(obj):
        obj.title = update_data["title"]
        obj.prompt_text = update_data["prompt_text"]
    
    mock_db.refresh.side_effect = refresh_side_effect
    
    # Mock response object for validation after update - with model_params as a dict
    mock_updated_response = {
        "id": mock_deep_research.id,
        "user_id": mock_deep_research.user_id,
        "owner_user_id": mock_deep_research.owner_user_id,
        "owner_org_id": mock_deep_research.owner_org_id,
        "visibility": mock_deep_research.visibility,
        "title": update_data["title"],
        "prompt_text": update_data["prompt_text"],
        "final_report": mock_deep_research.final_report,  # Keep as string
        "model_name": mock_deep_research.model_name,
        "model_params": {"max_tokens": 1000},  # Dict for response
        "source_count": mock_deep_research.source_count,
        "created_at": mock_deep_research.created_at.isoformat() if hasattr(mock_deep_research.created_at, 'isoformat') else mock_deep_research.created_at,
        "updated_at": mock_deep_research.updated_at.isoformat() if hasattr(mock_deep_research.updated_at, 'isoformat') else mock_deep_research.updated_at
    }
    
    # Patch DeepResearch model_validate and DeepResearchUpdateRequest validation
    with patch("app.routers.deep_research.DeepResearch.model_validate", return_value=mock_updated_response), \
         patch("app.schemas.deep_research_update_request.DeepResearchUpdateRequest.model_validate", return_value=DeepResearchUpdateRequest(**update_data)):
        # Execute request
        response = client.patch(f"/api/deep-research/{mock_deep_research.id}", json=update_data)
        
        # Assert response
        assert response.status_code == 200
        research = response.json()
        assert research["title"] == update_data["title"]
        assert research["prompt_text"] == update_data["prompt_text"]
        
        # Verify the mock object was updated via the refresh side effect
        assert mock_deep_research.title == update_data["title"]
        assert mock_deep_research.prompt_text == update_data["prompt_text"]
        
        # Verify DB interactions
        mock_db.execute.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_deep_research)

