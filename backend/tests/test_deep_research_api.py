# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import StrictInt  # noqa: F401
from typing import Any, List  # noqa: F401
from app.schemas.deep_research import DeepResearch  # noqa: F401
from app.schemas.deep_research_create_request import DeepResearchCreateRequest  # noqa: F401
from app.schemas.deep_research_update_request import DeepResearchUpdateRequest  # noqa: F401


def test_research_get(client: TestClient):
    """Test case for research_get

    List deep research items accessible to the user
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/research",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_research_id_delete(client: TestClient):
    """Test case for research_id_delete

    Delete a deep research item
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "DELETE",
    #    "/research/{id}".format(id=56),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_research_id_get(client: TestClient):
    """Test case for research_id_get

    Retrieve a single deep research item
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/research/{id}".format(id=56),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_research_id_patch(client: TestClient):
    """Test case for research_id_patch

    Update a deep research item
    """
    deep_research_update_request = {"final_report":"final_report","visibility":"visibility","title":"title"}

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "PATCH",
    #    "/research/{id}".format(id=56),
    #    headers=headers,
    #    json=deep_research_update_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_research_post(client: TestClient):
    """Test case for research_post

    Create a new deep research item
    """
    deep_research_create_request = {"final_report":"final_report","prompt_text":"prompt_text","visibility":"public","title":"title"}

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/research",
    #    headers=headers,
    #    json=deep_research_create_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

