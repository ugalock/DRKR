# coding: utf-8

from fastapi.testclient import TestClient


from typing import Any  # noqa: F401
from app.schemas.auth_login_request import AuthLoginRequest  # noqa: F401
from app.schemas.auth_login_response import AuthLoginResponse  # noqa: F401
from app.schemas.auth_refresh_request import AuthRefreshRequest  # noqa: F401
from app.schemas.auth_refresh_response import AuthRefreshResponse  # noqa: F401


def test_auth_login_post(client: TestClient):
    """Test case for auth_login_post

    User login
    """
    auth_login_request = {"password":"password","username":"username"}

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/auth/login",
    #    headers=headers,
    #    json=auth_login_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_auth_logout_post(client: TestClient):
    """Test case for auth_logout_post

    Logout user (invalidate token)
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/auth/logout",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_auth_refresh_post(client: TestClient):
    """Test case for auth_refresh_post

    Refresh access token
    """
    auth_refresh_request = {"refresh_token":"refresh_token"}

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/auth/refresh",
    #    headers=headers,
    #    json=auth_refresh_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

