# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import StrictInt
from typing import Any, List
from app.schemas.comment import Comment
from app.schemas.comment_create_request import CommentCreateRequest
from app.schemas.comment_update_request import CommentUpdateRequest


class BaseComments:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseComments.subclasses = BaseComments.subclasses + (cls,)
    async def comments_comment_id_delete(
        self,
        comment_id: StrictInt,
    ) -> None:
        ...


    async def comments_comment_id_patch(
        self,
        comment_id: StrictInt,
        comment_update_request: CommentUpdateRequest,
    ) -> Comment:
        ...


    async def research_id_comments_get(
        self,
        id: StrictInt,
    ) -> List[Comment]:
        ...


    async def research_id_comments_post(
        self,
        id: StrictInt,
        comment_create_request: CommentCreateRequest,
    ) -> Comment:
        ...
