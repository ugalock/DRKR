# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from app.routers.organizations_base import BaseOrganizations
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
from typing import Any, List
from app.schemas.org_membership_request import OrgMembershipRequest
from app.schemas.organization import Organization
from app.schemas.organization_create_request import OrganizationCreateRequest


router = APIRouter()

ns_pkg = app.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/orgs",
    responses={
        200: {"model": List[Organization], "description": "A list of organizations"},
    },
    tags=["organizations"],
    summary="List organizations visible to the user",
    response_model_by_alias=True,
)
async def orgs_get(
) -> List[Organization]:
    if not BaseOrganizations.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseOrganizations.subclasses[0]().orgs_get()


@router.get(
    "/orgs/{id}",
    responses={
        200: {"model": Organization, "description": "Organization retrieved"},
    },
    tags=["organizations"],
    summary="Get organization details",
    response_model_by_alias=True,
)
async def orgs_id_get(
    id: StrictInt = Path(..., description=""),
) -> Organization:
    if not BaseOrganizations.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseOrganizations.subclasses[0]().orgs_id_get(id)


@router.delete(
    "/orgs/{id}/members",
    responses={
        204: {"description": "User removed from org"},
    },
    tags=["organizations"],
    summary="Remove a user from the organization",
    response_model_by_alias=True,
)
async def orgs_id_members_delete(
    id: StrictInt = Path(..., description=""),
    user_id: StrictInt = Query(None, description="", alias="user_id"),
) -> None:
    if not BaseOrganizations.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseOrganizations.subclasses[0]().orgs_id_members_delete(id, user_id)


@router.post(
    "/orgs/{id}/members",
    responses={
        200: {"description": "User added to org"},
    },
    tags=["organizations"],
    summary="Add a user to the organization",
    response_model_by_alias=True,
)
async def orgs_id_members_post(
    id: StrictInt = Path(..., description=""),
    org_membership_request: OrgMembershipRequest = Body(None, description=""),
) -> None:
    if not BaseOrganizations.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseOrganizations.subclasses[0]().orgs_id_members_post(id, org_membership_request)


@router.post(
    "/orgs",
    responses={
        201: {"model": Organization, "description": "Organization created"},
    },
    tags=["organizations"],
    summary="Create a new organization",
    response_model_by_alias=True,
)
async def orgs_post(
    organization_create_request: OrganizationCreateRequest = Body(None, description=""),
) -> Organization:
    if not BaseOrganizations.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseOrganizations.subclasses[0]().orgs_post(organization_create_request)
