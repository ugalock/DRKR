# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from app.routers.comments_base import BaseComments
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
from app.schemas.comment import Comment
from app.schemas.comment_create_request import CommentCreateRequest
from app.schemas.comment_update_request import CommentUpdateRequest


router = APIRouter()

ns_pkg = app.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.delete(
    "/comments/{comment_id}",
    responses={
        204: {"description": "Comment deleted"},
    },
    tags=["comments"],
    summary="Delete a comment",
    response_model_by_alias=True,
)
async def comments_comment_id_delete(
    comment_id: StrictInt = Path(..., description=""),
) -> None:
    if not BaseComments.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseComments.subclasses[0]().comments_comment_id_delete(comment_id)


@router.patch(
    "/comments/{comment_id}",
    responses={
        200: {"model": Comment, "description": "Comment updated"},
    },
    tags=["comments"],
    summary="Update a comment",
    response_model_by_alias=True,
)
async def comments_comment_id_patch(
    comment_id: StrictInt = Path(..., description=""),
    comment_update_request: CommentUpdateRequest = Body(None, description=""),
) -> Comment:
    if not BaseComments.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseComments.subclasses[0]().comments_comment_id_patch(comment_id, comment_update_request)


@router.get(
    "/research/{id}/comments",
    responses={
        200: {"model": List[Comment], "description": "List of comments"},
    },
    tags=["comments"],
    summary="Get comments for a research item",
    response_model_by_alias=True,
)
async def research_id_comments_get(
    id: StrictInt = Path(..., description=""),
) -> List[Comment]:
    if not BaseComments.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseComments.subclasses[0]().research_id_comments_get(id)


@router.post(
    "/research/{id}/comments",
    responses={
        201: {"model": Comment, "description": "Comment created"},
    },
    tags=["comments"],
    summary="Add a comment to a research item",
    response_model_by_alias=True,
)
async def research_id_comments_post(
    id: StrictInt = Path(..., description=""),
    comment_create_request: CommentCreateRequest = Body(None, description=""),
) -> Comment:
    if not BaseComments.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseComments.subclasses[0]().research_id_comments_post(id, comment_create_request)
