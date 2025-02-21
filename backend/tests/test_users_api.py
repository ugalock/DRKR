# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import StrictInt  # noqa: F401
from typing import Any  # noqa: F401
from app.schemas.user import User  # noqa: F401
from app.schemas.user_create_request import UserCreateRequest  # noqa: F401
from app.schemas.user_update_request import UserUpdateRequest  # noqa: F401


def test_users_id_delete(client: TestClient):
    """Test case for users_id_delete

    Delete user account
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "DELETE",
    #    "/users/{id}".format(id=56),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_users_id_get(client: TestClient):
    """Test case for users_id_get

    Get a specific user by ID
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/users/{id}".format(id=56),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_users_id_patch(client: TestClient):
    """Test case for users_id_patch

    Update existing user data
    """
    user_update_request = {"display_name":"display_name","email":"email"}

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "PATCH",
    #    "/users/{id}".format(id=56),
    #    headers=headers,
    #    json=user_update_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_users_post(client: TestClient):
    """Test case for users_post

    Create a new user
    """
    user_create_request = {"password":"password","email":"email","username":"username"}

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/users",
    #    headers=headers,
    #    json=user_create_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

