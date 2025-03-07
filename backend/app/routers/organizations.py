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

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.schemas.extra_models import TokenModel  # noqa: F401
from pydantic import StrictInt
from typing import Any, List
from app.models import Organization as OrganizationModel, OrganizationMember as OrganizationMemberModel
from app.schemas.org_membership_request import OrgMembershipRequest
from app.schemas.organization import Organization
from app.schemas.organization_create_request import OrganizationCreateRequest
from app.db import get_db
from app.services.authentication import get_current_user
from app.schemas.org_member_role_update import OrgMemberRoleUpdate


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
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
) -> List[Organization]:
    # Get organizations where the user is a member
    query = (
        select(OrganizationModel)
        .join(OrganizationMemberModel)
        .where(OrganizationMemberModel.user_id == current_user.id)
        .options(selectinload(OrganizationModel.members))
    )
    
    result = await db.execute(query)
    organizations = result.scalars().all()
    
    return [Organization.model_validate(org) for org in organizations]


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
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Organization:
    # Get organization with members loaded
    query = (
        select(OrganizationModel)
        .where(OrganizationModel.id == id)
        .options(selectinload(OrganizationModel.members))
    )
    
    result = await db.execute(query)
    org = result.scalars().first()
    
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
        
    # Check if user is a member of the organization
    if not any(member.user_id == current_user.id for member in org.members):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return Organization.model_validate(org)


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
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
) -> None:
    # Check if the current user is an admin/owner of the organization OR if they're removing themselves
    is_self_removal = user_id == current_user.id
    
    if not is_self_removal:
        # Only check admin status if not removing self
        admin_query = (
            select(OrganizationMemberModel)
            .where(
                OrganizationMemberModel.organization_id == id,
                OrganizationMemberModel.user_id == current_user.id,
                OrganizationMemberModel.role.in_(["admin", "owner"])
            )
        )
        result = await db.execute(admin_query)
        admin_member = result.scalars().first()
        
        if not admin_member:
            raise HTTPException(status_code=403, detail="Only admins can remove other members")
    
    # Get the member to remove
    member_query = (
        select(OrganizationMemberModel)
        .where(
            OrganizationMemberModel.organization_id == id,
            OrganizationMemberModel.user_id == user_id
        )
    )
    result = await db.execute(member_query)
    member = result.scalars().first()
    
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    # Cannot remove the last owner
    if member.role == "owner":
        owner_count_query = (
            select(OrganizationMemberModel)
            .where(
                OrganizationMemberModel.organization_id == id,
                OrganizationMemberModel.role == "owner"
            )
        )
        result = await db.execute(owner_count_query)
        owners = result.scalars().all()
        if len(owners) <= 1:
            raise HTTPException(status_code=400, detail="Cannot remove the last owner")
    
    # Remove the member
    await db.delete(member)
    await db.commit()
    
    return Response(status_code=204)


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
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
) -> None:
    # Check if the current user is an admin/owner of the organization
    admin_query = (
        select(OrganizationMemberModel)
        .where(
            OrganizationMemberModel.organization_id == id,
            OrganizationMemberModel.user_id == current_user.id,
            OrganizationMemberModel.role.in_(["admin", "owner"])
        )
    )
    result = await db.execute(admin_query)
    admin_member = result.scalars().first()
    
    if not admin_member:
        raise HTTPException(status_code=403, detail="Only admins can add members")
    
    # Check if user is already a member
    existing_query = (
        select(OrganizationMemberModel)
        .where(
            OrganizationMemberModel.organization_id == id,
            OrganizationMemberModel.user_id == org_membership_request.user_id
        )
    )
    result = await db.execute(existing_query)
    existing_member = result.scalars().first()
    
    if existing_member:
        raise HTTPException(status_code=400, detail="User is already a member")
    
    # Create new member
    new_member = OrganizationMemberModel(
        organization_id=id,
        user_id=org_membership_request.user_id,
        role=org_membership_request.role or "member"
    )
    
    db.add(new_member)
    await db.commit()
    
    return Response(status_code=200)


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
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Organization:
    # Create the organization
    new_org = OrganizationModel(
        name=organization_create_request.name,
        description=organization_create_request.description
    )
    
    db.add(new_org)
    await db.flush()  # This assigns the ID to new_org
    
    # Add the current user as an owner
    owner_member = OrganizationMemberModel(
        organization_id=new_org.id,
        user_id=current_user.id,
        role="owner"
    )
    
    db.add(owner_member)
    await db.commit()
    
    # Reload the organization with members
    query = (
        select(OrganizationModel)
        .where(OrganizationModel.id == new_org.id)
        .options(selectinload(OrganizationModel.members))
    )
    
    result = await db.execute(query)
    org = result.scalars().first()
    
    return Organization.model_validate(org)


@router.patch(
    "/orgs/{id}/members/{user_id}",
    responses={
        200: {"description": "Member role updated"},
    },
    tags=["organizations"],
    summary="Update a member's role in the organization",
    response_model_by_alias=True,
)
async def orgs_id_members_user_id_patch(
    id: StrictInt = Path(..., description="Organization ID"),
    user_id: StrictInt = Path(..., description="User ID to update"),
    role_update: OrgMemberRoleUpdate = Body(None, description="New role"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
) -> dict:
    # Permission checks and role validation
    if role_update.role not in ["member", "admin", "owner"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    # Check if the current user is a member of the organization
    user_role_query = (
        select(OrganizationMemberModel)
        .where(
            OrganizationMemberModel.organization_id == id,
            OrganizationMemberModel.user_id == current_user.id
        )
    )
    result = await db.execute(user_role_query)
    current_user_role = result.scalars().first()
    if current_user_role is None:
        raise HTTPException(status_code=403, detail="You are not a member of this organization")
    is_owner = current_user_role.role == "owner"
    is_admin = current_user_role.role == "admin"
    
    # Get the member to update
    member_query = (
        select(OrganizationMemberModel)
        .where(
            OrganizationMemberModel.organization_id == id,
            OrganizationMemberModel.user_id == user_id
        )
    )
    result = await db.execute(member_query)
    member = result.scalars().first()
    
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    current_role = member.role
    new_role = role_update.role
    
    # Owner checks
    if current_role == "owner" and new_role != "owner" and not is_owner:
        raise HTTPException(status_code=403, detail="Only owners can demote other owners")
    
    # Admin checks
    if current_role == "admin":
        if new_role == "owner" and not is_owner:
            raise HTTPException(status_code=403, detail="Only owners can promote to owner")
        if new_role == "member" and not (is_owner or is_admin):
            raise HTTPException(status_code=403, detail="Only admins or owners can demote admins")
    
    # Member checks
    if current_role == "member":
        if new_role == "owner" and not is_owner:
            raise HTTPException(status_code=403, detail="Only owners can promote to owner")
        if new_role == "admin" and not (is_owner or is_admin):
            raise HTTPException(status_code=403, detail="Only admins or owners can promote to admin")
    
    # Cannot change your own role if you're the last owner
    if current_role == "owner" and member.user_id == current_user.id and new_role != "owner":
        owner_count_query = (
            select(OrganizationMemberModel)
            .where(
                OrganizationMemberModel.organization_id == id,
                OrganizationMemberModel.role == "owner"
            )
        )
        result = await db.execute(owner_count_query)
        owners = result.scalars().all()
        if len(owners) <= 1:
            raise HTTPException(status_code=400, detail="Cannot demote the last owner")
    
    # Update the role
    member.role = new_role
    await db.commit()
    
    return {"message": f"Member role updated to {new_role}"}
