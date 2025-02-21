# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from app.routers.auth_base import BaseAuth
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
from typing import Any
from app.schemas.auth_login_request import AuthLoginRequest
from app.schemas.auth_login_response import AuthLoginResponse
from app.schemas.auth_refresh_request import AuthRefreshRequest
from app.schemas.auth_refresh_response import AuthRefreshResponse


router = APIRouter()

ns_pkg = app.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.post(
    "/auth/login",
    responses={
        200: {"model": AuthLoginResponse, "description": "Successful login"},
    },
    tags=["auth"],
    summary="User login",
    response_model_by_alias=True,
)
async def auth_login_post(
    auth_login_request: AuthLoginRequest = Body(None, description=""),
) -> AuthLoginResponse:
    if not BaseAuth.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAuth.subclasses[0]().auth_login_post(auth_login_request)


@router.post(
    "/auth/logout",
    responses={
        204: {"description": "Logout successful"},
    },
    tags=["auth"],
    summary="Logout user (invalidate token)",
    response_model_by_alias=True,
)
async def auth_logout_post(
) -> None:
    if not BaseAuth.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAuth.subclasses[0]().auth_logout_post()


@router.post(
    "/auth/refresh",
    responses={
        200: {"model": AuthRefreshResponse, "description": "Token refreshed"},
    },
    tags=["auth"],
    summary="Refresh access token",
    response_model_by_alias=True,
)
async def auth_refresh_post(
    auth_refresh_request: AuthRefreshRequest = Body(None, description=""),
) -> AuthRefreshResponse:
    if not BaseAuth.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAuth.subclasses[0]().auth_refresh_post(auth_refresh_request)
