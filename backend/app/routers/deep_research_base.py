# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import StrictInt
from typing import Any, List
from app.schemas.deep_research import DeepResearch
from app.schemas.deep_research_create_request import DeepResearchCreateRequest
from app.schemas.deep_research_update_request import DeepResearchUpdateRequest


class BaseDeepResearch:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseDeepResearch.subclasses = BaseDeepResearch.subclasses + (cls,)
    async def research_get(
        self,
    ) -> List[DeepResearch]:
        ...


    async def research_id_delete(
        self,
        id: StrictInt,
    ) -> None:
        ...


    async def research_id_get(
        self,
        id: StrictInt,
    ) -> DeepResearch:
        ...


    async def research_id_patch(
        self,
        id: StrictInt,
        deep_research_update_request: DeepResearchUpdateRequest,
    ) -> DeepResearch:
        ...


    async def research_post(
        self,
        deep_research_create_request: DeepResearchCreateRequest,
    ) -> DeepResearch:
        ...
