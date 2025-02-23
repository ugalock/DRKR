# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import StrictInt
from app.schemas.user import User
from app.schemas.user_create_request import UserCreateRequest
from app.schemas.user_update_request import UserUpdateRequest


class BaseUsers:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseUsers.subclasses = BaseUsers.subclasses + (cls,)

    async def users_id_delete(
        self,
        id: StrictInt,
    ) -> None:
        ...

    async def users_id_get(
        self,
        id: StrictInt,
    ) -> User:
        ...

    async def users_id_patch(
        self,
        id: StrictInt,
        user_update_request: UserUpdateRequest,
    ) -> User:
        ...
