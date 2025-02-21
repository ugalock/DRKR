# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from app.routers.tags_base import BaseTags
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
from app.schemas.tag import Tag
from app.schemas.tag_create_request import TagCreateRequest
from app.schemas.tag_update_request import TagUpdateRequest


router = APIRouter()

ns_pkg = app.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/tags",
    responses={
        200: {"model": List[Tag], "description": "List of tags"},
    },
    tags=["tags"],
    summary="List all tags (global, org, or user-specific) accessible to the user",
    response_model_by_alias=True,
)
async def tags_get(
) -> List[Tag]:
    if not BaseTags.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseTags.subclasses[0]().tags_get()


@router.delete(
    "/tags/{id}",
    responses={
        204: {"description": "Tag removed"},
    },
    tags=["tags"],
    summary="Delete a tag",
    response_model_by_alias=True,
)
async def tags_id_delete(
    id: StrictInt = Path(..., description=""),
) -> None:
    if not BaseTags.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseTags.subclasses[0]().tags_id_delete(id)


@router.get(
    "/tags/{id}",
    responses={
        200: {"model": Tag, "description": "Tag data"},
    },
    tags=["tags"],
    summary="Retrieve a specific tag",
    response_model_by_alias=True,
)
async def tags_id_get(
    id: StrictInt = Path(..., description=""),
) -> Tag:
    if not BaseTags.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseTags.subclasses[0]().tags_id_get(id)


@router.patch(
    "/tags/{id}",
    responses={
        200: {"model": Tag, "description": "Tag updated"},
    },
    tags=["tags"],
    summary="Update an existing tag",
    response_model_by_alias=True,
)
async def tags_id_patch(
    id: StrictInt = Path(..., description=""),
    tag_update_request: TagUpdateRequest = Body(None, description=""),
) -> Tag:
    if not BaseTags.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseTags.subclasses[0]().tags_id_patch(id, tag_update_request)


@router.get(
    "/tags/{id}/research",
    responses={
        200: {"model": List[DeepResearch], "description": "List of research items"},
    },
    tags=["tags"],
    summary="List research items associated with a particular tag",
    response_model_by_alias=True,
)
async def tags_id_research_get(
    id: StrictInt = Path(..., description=""),
) -> List[DeepResearch]:
    if not BaseTags.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseTags.subclasses[0]().tags_id_research_get(id)


@router.post(
    "/tags",
    responses={
        201: {"model": Tag, "description": "Tag created"},
    },
    tags=["tags"],
    summary="Create a new tag",
    response_model_by_alias=True,
)
async def tags_post(
    tag_create_request: TagCreateRequest = Body(None, description=""),
) -> Tag:
    if not BaseTags.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseTags.subclasses[0]().tags_post(tag_create_request)
