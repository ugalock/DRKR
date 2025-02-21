# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from typing import Any
from app.schemas.auth_login_request import AuthLoginRequest
from app.schemas.auth_login_response import AuthLoginResponse
from app.schemas.auth_refresh_request import AuthRefreshRequest
from app.schemas.auth_refresh_response import AuthRefreshResponse


class BaseAuth:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseAuth.subclasses = BaseAuth.subclasses + (cls,)
    async def auth_login_post(
        self,
        auth_login_request: AuthLoginRequest,
    ) -> AuthLoginResponse:
        ...


    async def auth_logout_post(
        self,
    ) -> None:
        ...


    async def auth_refresh_post(
        self,
        auth_refresh_request: AuthRefreshRequest,
    ) -> AuthRefreshResponse:
        ...
