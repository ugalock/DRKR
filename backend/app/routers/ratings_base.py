# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import StrictInt
from typing import List
from app.schemas.rating import Rating
from app.schemas.rating_create_request import RatingCreateRequest


class BaseRatings:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseRatings.subclasses = BaseRatings.subclasses + (cls,)
    async def research_id_ratings_get(
        self,
        id: StrictInt,
    ) -> List[Rating]:
        ...


    async def research_id_ratings_post(
        self,
        id: StrictInt,
        rating_create_request: RatingCreateRequest,
    ) -> Rating:
        ...
