# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import StrictInt  # noqa: F401
from typing import Any, List  # noqa: F401
from app.schemas.org_membership_request import OrgMembershipRequest  # noqa: F401
from app.schemas.organization import Organization  # noqa: F401
from app.schemas.organization_create_request import OrganizationCreateRequest  # noqa: F401


def test_orgs_get(client: TestClient):
    """Test case for orgs_get

    List organizations visible to the user
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/orgs",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_orgs_id_get(client: TestClient):
    """Test case for orgs_id_get

    Get organization details
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/orgs/{id}".format(id=56),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_orgs_id_members_delete(client: TestClient):
    """Test case for orgs_id_members_delete

    Remove a user from the organization
    """
    params = [("user_id", 56)]
    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "DELETE",
    #    "/orgs/{id}/members".format(id=56),
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_orgs_id_members_post(client: TestClient):
    """Test case for orgs_id_members_post

    Add a user to the organization
    """
    org_membership_request = {"role":"role","user_id":0}

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/orgs/{id}/members".format(id=56),
    #    headers=headers,
    #    json=org_membership_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_orgs_post(client: TestClient):
    """Test case for orgs_post

    Create a new organization
    """
    organization_create_request = {"name":"name","description":"description"}

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/orgs",
    #    headers=headers,
    #    json=organization_create_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

