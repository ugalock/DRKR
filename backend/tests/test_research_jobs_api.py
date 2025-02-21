# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import StrictStr  # noqa: F401
from app.schemas.research_job import ResearchJob  # noqa: F401
from app.schemas.research_job_create_request import ResearchJobCreateRequest  # noqa: F401


def test_research_jobs_job_id_get(client: TestClient):
    """Test case for research_jobs_job_id_get

    Poll status of a background research job
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/research-jobs/{job_id}".format(job_id='job_id_example'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_research_jobs_post(client: TestClient):
    """Test case for research_jobs_post

    Launch a new background research job
    """
    research_job_create_request = {"prompt_text":"prompt_text","model_params":"{}"}

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/research-jobs",
    #    headers=headers,
    #    json=research_job_create_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

