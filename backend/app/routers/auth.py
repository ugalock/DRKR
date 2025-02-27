# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from datetime import datetime, timedelta
import secrets
import requests

from fastapi import (
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
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2AuthorizationCodeBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, Optional

from app.routers.auth_base import BaseAuth
from app.schemas.extra_models import TokenModel  # noqa: F401
from app.schemas.auth_login_request import AuthLoginRequest
from app.schemas.auth_login_response import AuthLoginResponse
from app.schemas.auth_refresh_request import AuthRefreshRequest
from app.schemas.auth_refresh_response import AuthRefreshResponse
from app.schemas.auth_token_response import AuthTokenResponse

from app.db import get_db
from app.models import User
from app.services.authentication import (
    create_jwt_token,
    get_current_user,
    verify_api_key
)
from app.config import settings
import app.impl

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


@router.post(
    "/auth/token",
    responses={
        200: {"model": AuthTokenResponse, "description": "Access token obtained"},
    },
    tags=["auth"],
    summary="Exchange Auth0 code for access token",
    response_model_by_alias=True,
)
async def login_for_access_token(
    code: str
) -> AuthTokenResponse:
    """Exchange Auth0 code for access token"""

    token_url = f"https://{settings.AUTH0_DOMAIN}/oauth/token"
    payload = {
        "grant_type": "authorization_code",
        "client_id": settings.AUTH0_CLIENT_ID,
        "client_secret": settings.AUTH0_CLIENT_SECRET,
        "code": code,
        "redirect_uri": settings.AUTH0_CALLBACK_URL,
    }
    response = requests.post(token_url, json=payload)
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Failed to exchange code for token: {response.text}"
        )
    token_data = response.json()
    return AuthTokenResponse(
        access_token=token_data.get("access_token"),
        token_type=token_data.get("token_type"),
        expires_in=token_data.get("expires_in"),
        refresh_token=token_data.get("refresh_token"),
        id_token=token_data.get("id_token")
    )

@router.get(
    "/callback",
    responses={
        302: {"description": "Redirect to dashboard after successful token exchange"},
    },
    tags=["auth"],
    summary="Auth0 callback endpoint",
)
async def auth_callback(
    code: str = Query(..., description="Authorization code from Auth0"),
    state: str = Query(..., description="State parameter for CSRF protection"),
    auth_state: Optional[str] = Cookie(None, alias="auth_state"),
    db: AsyncSession = Depends(get_db)
) -> RedirectResponse:
    """
    Callback endpoint to handle the redirect from Auth0 after a successful login.

    This endpoint receives the authorization code and state. It validates the state against the
    stored cookie (auth_state) and then exchanges the code for tokens. Finally, it redirects the user
    to the frontend dashboard.
    """
    # Validate the state parameter
    if auth_state is None or state != auth_state:
        raise HTTPException(status_code=400, detail="Invalid state parameter")

    # Exchange the authorization code for tokens
    token_response = await login_for_access_token(code=code)

    # In a production app, you might store tokens in secure cookies or session here.
    # For demonstration, we set a cookie for the access token.
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie("access_token", token_response.access_token, httponly=True, secure=True)
    response.set_cookie("id_token", token_response.id_token, httponly=True, secure=True)
    # Optionally clear the auth_state cookie after validation
    response.delete_cookie("auth_state")
    return response