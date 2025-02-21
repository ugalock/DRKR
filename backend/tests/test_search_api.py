# coding: utf-8

from fastapi.testclient import TestClient


from typing import List  # noqa: F401
from app.schemas.deep_research import DeepResearch  # noqa: F401
from app.schemas.search_request import SearchRequest  # noqa: F401


def test_search_post(client: TestClient):
    """Test case for search_post

    Perform semantic or advanced search
    """
    search_request = {"query":"query","top_k":0}

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/search",
    #    headers=headers,
    #    json=search_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

