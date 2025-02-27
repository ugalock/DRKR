# coding: utf-8

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
import json
from datetime import datetime, timezone
from fastapi import HTTPException

from pydantic import StrictStr  # noqa: F401
from app.schemas.research_job import ResearchJob  # noqa: F401
from app.schemas.research_job_create_request import ResearchJobCreateRequest  # noqa: F401
from app.models import ResearchJob as ResearchJobModel, User

@pytest.fixture
def mock_research_job():
    """Fixture for a mock research job"""
    now = datetime.now(timezone.utc).isoformat()  # ISO format string
    return ResearchJobModel(
        id="1",  # String
        job_id="job-123",
        user_id="1",  # String
        status="completed",
        service="opendr",
        model_name="gpt-4",
        visibility="private",
        created_at=now,
        updated_at=now,
        model_params={"model": "gpt-4", "max_tokens": 1000},
        deep_research_id=None,
        owner_org_id=None,
        owner_user_id=None
    )

@pytest.fixture
def mock_pending_job():
    """Fixture for a pending research job"""
    now = datetime.now(timezone.utc).isoformat()  # ISO format string
    return ResearchJobModel(
        id="2",  # String
        job_id="job-456",
        user_id="1",  # String
        status="running",  # Valid enum value
        service="opendr",
        model_name="gpt-4",
        visibility="private",
        created_at=now,
        updated_at=now,
        model_params={"model": "gpt-4", "max_tokens": 1000},
        deep_research_id=None,
        owner_org_id=None,
        owner_user_id=None
    )

def test_research_jobs_post(client, mock_db, mock_user):
    """Test creating a new research job"""
    # Setup DB mocks
    mock_db.add = AsyncMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    
    # Create a valid DB model object that matches what's expected
    now = datetime.now(timezone.utc).isoformat()  # ISO format string
    mock_job_model = ResearchJobModel(
        id="1",  # String
        job_id="job-123",
        user_id=str(mock_user.id),  # String
        status="pending_answers",
        service="opendr",
        model_name="gpt-4",
        visibility="private",
        model_params={"model": "gpt-4", "max_tokens": 2000},
        created_at=now,
        updated_at=now,
        deep_research_id=None,
        owner_org_id=None,
        owner_user_id=None
    )
    
    # Mock the validate_service method so it doesn't cause an error
    with patch("app.services.research.ResearchService._validate_service", new_callable=AsyncMock) as mock_validate:
        # Mock the start_job method
        with patch("app.services.research.ResearchService.start_job", new_callable=AsyncMock) as mock_start_job:
            # Create test job request with required fields
            job_request = {
                "service": "opendr",
                "prompt": "Research the impact of AI on healthcare",
                "model": "gpt-4",
                "model_params": {"model": "gpt-4", "max_tokens": 2000}
            }
            
            # Setup the mock start_job to return a dictionary with the job key
            mock_start_job.return_value = {"job": mock_job_model}
            
            # Mock check_research_job_permissions to return True
            with patch("app.routers.research_jobs.check_research_job_permissions", return_value=True):
                # Execute request
                response = client.post("/api/research-jobs", json=job_request)
                
                # Verify the response
                assert response.status_code == 201
                response_json = response.json()
                assert "job_id" in response_json
                assert response_json["job_id"] == "job-123"
                assert response_json["status"] == "pending_answers"
                assert response_json["service"] == "opendr"
                assert response_json["model_name"] == "gpt-4"

def test_research_jobs_job_id_get(client, mock_db, mock_user, mock_research_job):
    """Test getting a specific research job"""
    # Mock the poll_status method to return proper job model
    with patch("app.services.research.ResearchService.poll_status", new_callable=AsyncMock) as mock_poll:
        # Set up the mock to return the actual model object
        mock_poll.return_value = {
            "job": mock_research_job,  # Return the actual model object
            "results": {"data": "some result data"}
        }
        
        # Mock the permission check to return True
        with patch("app.routers.research_jobs.check_research_job_permissions", return_value=True):
            # Execute request
            response = client.post(f"/api/research-jobs/get", json={"id": str(mock_research_job.id)})
            
            # Verify the response
            assert response.status_code == 200
            response_json = response.json()
            assert "job_id" in response_json
            assert response_json["job_id"] == "job-123"
            assert response_json["status"] == "completed"
            assert response_json["service"] == "opendr"
            assert response_json["model_name"] == "gpt-4"

def test_research_jobs_job_id_get_not_found(client, mock_db, mock_user):
    """Test getting a research job that doesn't exist"""
    
    # Mock the poll_status method to raise a 404 exception
    with patch("app.services.research.ResearchService.poll_status", new_callable=AsyncMock) as mock_poll:
        # Configure the mock to raise an HTTPException with 404 status
        mock_poll.side_effect = HTTPException(status_code=404, detail="Research job not found")
        
        # Execute request
        response = client.post("/api/research-jobs/get", json={"id": "999"})
        
        # Verify the response
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

def test_research_jobs_job_id_get_pending(client, mock_db, mock_user, mock_pending_job):
    """Test getting a pending research job without Celery task check"""
    # Mock the poll_status method to return proper job model
    with patch("app.services.research.ResearchService.poll_status", new_callable=AsyncMock) as mock_poll:
        # Set up the mock with results for a pending job
        mock_poll.return_value = {
            "job": mock_pending_job,  # Return the actual model
            "results": {
                "status": "running",
                "progress": 25
            }
        }
        
        # Mock the permission check to return True
        with patch("app.routers.research_jobs.check_research_job_permissions", return_value=True):
            # Execute request
            response = client.post(f"/api/research-jobs/get", json={"id": str(mock_pending_job.id)})
            
            # Verify the response
            assert response.status_code == 200
            response_json = response.json()
            assert "job_id" in response_json
            assert response_json["job_id"] == "job-456"
            assert response_json["status"] == "running"
            assert response_json["service"] == "opendr"
            assert response_json["model_name"] == "gpt-4"

