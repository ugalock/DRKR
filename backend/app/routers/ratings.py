# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from app.routers.ratings_base import BaseRatings
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
from pydantic import StrictInt
from typing import List
from app.schemas.rating import Rating
from app.schemas.rating_create_request import RatingCreateRequest


router = APIRouter()

ns_pkg = app.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/research/{id}/ratings",
    responses={
        200: {"model": List[Rating], "description": "Ratings retrieved"},
    },
    tags=["ratings"],
    summary="Get ratings for a research item",
    response_model_by_alias=True,
)
async def research_id_ratings_get(
    id: StrictInt = Path(..., description=""),
) -> List[Rating]:
    if not BaseRatings.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseRatings.subclasses[0]().research_id_ratings_get(id)


@router.post(
    "/research/{id}/ratings",
    responses={
        201: {"model": Rating, "description": "Rating created or updated"},
    },
    tags=["ratings"],
    summary="Add or update a rating for a research item",
    response_model_by_alias=True,
)
async def research_id_ratings_post(
    id: StrictInt = Path(..., description=""),
    rating_create_request: RatingCreateRequest = Body(None, description=""),
) -> Rating:
    if not BaseRatings.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseRatings.subclasses[0]().research_id_ratings_post(id, rating_create_request)
