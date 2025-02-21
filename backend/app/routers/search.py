# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from app.routers.search_base import BaseSearch
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
from typing import List
from app.schemas.deep_research import DeepResearch
from app.schemas.search_request import SearchRequest


router = APIRouter()

ns_pkg = app.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.post(
    "/search",
    responses={
        200: {"model": List[DeepResearch], "description": "Search results"},
    },
    tags=["search"],
    summary="Perform semantic or advanced search",
    response_model_by_alias=True,
)
async def search_post(
    search_request: SearchRequest = Body(None, description=""),
) -> List[DeepResearch]:
    if not BaseSearch.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseSearch.subclasses[0]().search_post(search_request)
