# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import StrictInt  # noqa: F401
from typing import List  # noqa: F401
from app.schemas.rating import Rating  # noqa: F401
from app.schemas.rating_create_request import RatingCreateRequest  # noqa: F401


def test_research_id_ratings_get(client: TestClient):
    """Test case for research_id_ratings_get

    Get ratings for a research item
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/research/{id}/ratings".format(id=56),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_research_id_ratings_post(client: TestClient):
    """Test case for research_id_ratings_post

    Add or update a rating for a research item
    """
    rating_create_request = {"rating_value":0}

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/research/{id}/ratings".format(id=56),
    #    headers=headers,
    #    json=rating_create_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

