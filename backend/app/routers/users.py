# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from app.routers.users_base import BaseUsers
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
from typing import Any
from app.schemas.user import User
from app.schemas.user_create_request import UserCreateRequest
from app.schemas.user_update_request import UserUpdateRequest


router = APIRouter()

ns_pkg = app.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.delete(
    "/users/{id}",
    responses={
        204: {"description": "User deleted"},
    },
    tags=["users"],
    summary="Delete user account",
    response_model_by_alias=True,
)
async def users_id_delete(
    id: StrictInt = Path(..., description=""),
) -> None:
    if not BaseUsers.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseUsers.subclasses[0]().users_id_delete(id)


@router.get(
    "/users/{id}",
    responses={
        200: {"model": User, "description": "User data retrieved"},
    },
    tags=["users"],
    summary="Get a specific user by ID",
    response_model_by_alias=True,
)
async def users_id_get(
    id: StrictInt = Path(..., description=""),
) -> User:
    if not BaseUsers.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseUsers.subclasses[0]().users_id_get(id)


@router.patch(
    "/users/{id}",
    responses={
        200: {"model": User, "description": "User updated"},
    },
    tags=["users"],
    summary="Update existing user data",
    response_model_by_alias=True,
)
async def users_id_patch(
    id: StrictInt = Path(..., description=""),
    user_update_request: UserUpdateRequest = Body(None, description=""),
) -> User:
    if not BaseUsers.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseUsers.subclasses[0]().users_id_patch(id, user_update_request)


@router.post(
    "/users",
    responses={
        201: {"model": User, "description": "User created"},
    },
    tags=["users"],
    summary="Create a new user",
    response_model_by_alias=True,
)
async def users_post(
    user_create_request: UserCreateRequest = Body(None, description=""),
) -> User:
    if not BaseUsers.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseUsers.subclasses[0]().users_post(user_create_request)
