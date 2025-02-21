# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import StrictInt  # noqa: F401
from typing import Any, List  # noqa: F401
from app.schemas.comment import Comment  # noqa: F401
from app.schemas.comment_create_request import CommentCreateRequest  # noqa: F401
from app.schemas.comment_update_request import CommentUpdateRequest  # noqa: F401


def test_comments_comment_id_delete(client: TestClient):
    """Test case for comments_comment_id_delete

    Delete a comment
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "DELETE",
    #    "/comments/{comment_id}".format(comment_id=56),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_comments_comment_id_patch(client: TestClient):
    """Test case for comments_comment_id_patch

    Update a comment
    """
    comment_update_request = {"comment_text":"comment_text"}

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "PATCH",
    #    "/comments/{comment_id}".format(comment_id=56),
    #    headers=headers,
    #    json=comment_update_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_research_id_comments_get(client: TestClient):
    """Test case for research_id_comments_get

    Get comments for a research item
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/research/{id}/comments".format(id=56),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_research_id_comments_post(client: TestClient):
    """Test case for research_id_comments_post

    Add a comment to a research item
    """
    comment_create_request = {"comment_text":"comment_text"}

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/research/{id}/comments".format(id=56),
    #    headers=headers,
    #    json=comment_create_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

