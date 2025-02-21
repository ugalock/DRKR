# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import StrictInt
from typing import Any, List
from app.schemas.deep_research import DeepResearch
from app.schemas.tag import Tag
from app.schemas.tag_create_request import TagCreateRequest
from app.schemas.tag_update_request import TagUpdateRequest


class BaseTags:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseTags.subclasses = BaseTags.subclasses + (cls,)
    async def tags_get(
        self,
    ) -> List[Tag]:
        ...


    async def tags_id_delete(
        self,
        id: StrictInt,
    ) -> None:
        ...


    async def tags_id_get(
        self,
        id: StrictInt,
    ) -> Tag:
        ...


    async def tags_id_patch(
        self,
        id: StrictInt,
        tag_update_request: TagUpdateRequest,
    ) -> Tag:
        ...


    async def tags_id_research_get(
        self,
        id: StrictInt,
    ) -> List[DeepResearch]:
        ...


    async def tags_post(
        self,
        tag_create_request: TagCreateRequest,
    ) -> Tag:
        ...
