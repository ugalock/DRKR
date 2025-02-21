# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from app.routers.research_jobs_base import BaseResearchJobs
import app.impl

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
)

from app.schemas.extra_models import TokenModel  # noqa: F401
from pydantic import StrictStr
from app.schemas.research_job import ResearchJob
from app.schemas.research_job_create_request import ResearchJobCreateRequest


router = APIRouter()

ns_pkg = app.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/research-jobs/{job_id}",
    responses={
        200: {"model": ResearchJob, "description": "Research job status"},
    },
    tags=["research-jobs"],
    summary="Poll status of a background research job",
    response_model_by_alias=True,
)
async def research_jobs_job_id_get(
    job_id: StrictStr = Path(..., description=""),
) -> ResearchJob:
    if not BaseResearchJobs.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseResearchJobs.subclasses[0]().research_jobs_job_id_get(job_id)


@router.post(
    "/research-jobs",
    responses={
        201: {"model": ResearchJob, "description": "Research job started"},
    },
    tags=["research-jobs"],
    summary="Launch a new background research job",
    response_model_by_alias=True,
)
async def research_jobs_post(
    research_job_create_request: ResearchJobCreateRequest = Body(None, description=""),
) -> ResearchJob:
    if not BaseResearchJobs.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseResearchJobs.subclasses[0]().research_jobs_post(research_job_create_request)
