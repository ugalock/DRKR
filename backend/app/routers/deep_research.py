# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from app.routers.deep_research_base import BaseDeepResearch
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
from pydantic import StrictInt
from typing import Any, List
from app.schemas.deep_research import DeepResearch
from app.schemas.deep_research_create_request import DeepResearchCreateRequest
from app.schemas.deep_research_update_request import DeepResearchUpdateRequest


router = APIRouter()

ns_pkg = app.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/research",
    responses={
        200: {"model": List[DeepResearch], "description": "A list of deep research items"},
    },
    tags=["deep-research"],
    summary="List deep research items accessible to the user",
    response_model_by_alias=True,
)
async def research_get(
) -> List[DeepResearch]:
    if not BaseDeepResearch.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDeepResearch.subclasses[0]().research_get()


@router.delete(
    "/research/{id}",
    responses={
        204: {"description": "Research item deleted"},
    },
    tags=["deep-research"],
    summary="Delete a deep research item",
    response_model_by_alias=True,
)
async def research_id_delete(
    id: StrictInt = Path(..., description=""),
) -> None:
    if not BaseDeepResearch.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDeepResearch.subclasses[0]().research_id_delete(id)


@router.get(
    "/research/{id}",
    responses={
        200: {"model": DeepResearch, "description": "Research item data"},
    },
    tags=["deep-research"],
    summary="Retrieve a single deep research item",
    response_model_by_alias=True,
)
async def research_id_get(
    id: StrictInt = Path(..., description=""),
) -> DeepResearch:
    if not BaseDeepResearch.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDeepResearch.subclasses[0]().research_id_get(id)


@router.patch(
    "/research/{id}",
    responses={
        200: {"model": DeepResearch, "description": "Research item updated"},
    },
    tags=["deep-research"],
    summary="Update a deep research item",
    response_model_by_alias=True,
)
async def research_id_patch(
    id: StrictInt = Path(..., description=""),
    deep_research_update_request: DeepResearchUpdateRequest = Body(None, description=""),
) -> DeepResearch:
    if not BaseDeepResearch.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDeepResearch.subclasses[0]().research_id_patch(id, deep_research_update_request)


@router.post(
    "/research",
    responses={
        201: {"model": DeepResearch, "description": "Deep research item created"},
    },
    tags=["deep-research"],
    summary="Create a new deep research item",
    response_model_by_alias=True,
)
async def research_post(
    deep_research_create_request: DeepResearchCreateRequest = Body(None, description=""),
) -> DeepResearch:
    if not BaseDeepResearch.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDeepResearch.subclasses[0]().research_post(deep_research_create_request)
