# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from typing import List
from app.schemas.deep_research import DeepResearch
from app.schemas.search_request import SearchRequest


class BaseSearch:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseSearch.subclasses = BaseSearch.subclasses + (cls,)
    async def search_post(
        self,
        search_request: SearchRequest,
    ) -> List[DeepResearch]:
        ...
