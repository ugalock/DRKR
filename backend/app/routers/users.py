# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil
from pydantic import StrictInt
from sqlalchemy.orm import Session
from typing import Any
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

import app.impl
from app.db import get_db
from app.routers.users_base import BaseUsers
from app.schemas.extra_models import TokenModel  # noqa: F401
from app.schemas.user import User
from app.schemas.user_create_request import UserCreateRequest
from app.schemas.user_update_request import UserUpdateRequest
from app.services.authentication import get_current_user, verify_jwt_token, oauth2_scheme


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
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    payload = await verify_jwt_token(token)
    

@router.get(
    "/users/me",
    responses={
        200: {"model": User, "description": "User data retrieved"},
    },
    tags=["users"],
    summary="Get the current user",
    response_model_by_alias=True,
)
async def users_me_get(
    current_user: User = Depends(get_current_user),
) -> User:
    return current_user

@router.patch(
    "/users/me",
    responses={
        200: {"model": User, "description": "User updated"},
    },
    tags=["users"],
    summary="Update the current user",
    response_model_by_alias=True,
)
async def users_me_patch(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    user_update_request: UserUpdateRequest = Body(None, description=""),
) -> User:
    user = db.query(User).filter(User.id == current_user.id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user.email = user_update_request.email or user.email
    user.display_name = user_update_request.display_name or user.display_name
    db.commit()
    db.refresh(user)
    return user