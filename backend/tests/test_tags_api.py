# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import StrictInt  # noqa: F401
from typing import Any, List  # noqa: F401
from app.schemas.deep_research import DeepResearch  # noqa: F401
from app.schemas.tag import Tag  # noqa: F401
from app.schemas.tag_create_request import TagCreateRequest  # noqa: F401
from app.schemas.tag_update_request import TagUpdateRequest  # noqa: F401


def test_tags_get(client: TestClient):
    """Test case for tags_get

    List all tags (global, org, or user-specific) accessible to the user
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/tags",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_tags_id_delete(client: TestClient):
    """Test case for tags_id_delete

    Delete a tag
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "DELETE",
    #    "/tags/{id}".format(id=56),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_tags_id_get(client: TestClient):
    """Test case for tags_id_get

    Retrieve a specific tag
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/tags/{id}".format(id=56),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_tags_id_patch(client: TestClient):
    """Test case for tags_id_patch

    Update an existing tag
    """
    tag_update_request = {"name":"name","is_global":1}

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "PATCH",
    #    "/tags/{id}".format(id=56),
    #    headers=headers,
    #    json=tag_update_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_tags_id_research_get(client: TestClient):
    """Test case for tags_id_research_get

    List research items associated with a particular tag
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/tags/{id}/research".format(id=56),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_tags_post(client: TestClient):
    """Test case for tags_post

    Create a new tag
    """
    tag_create_request = {"user_id":6,"organization_id":0,"name":"name","is_global":1}

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/tags",
    #    headers=headers,
    #    json=tag_create_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

