# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil
from pydantic import StrictInt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import Any, Optional
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

import app.impl
from app.db import get_db
from app.models import OrganizationMember, User as UserModel
from app.routers.users_base import BaseUsers
from app.schemas.user import User
from app.schemas.user_update_request import UserUpdateRequest
from app.services.authentication import get_current_user, verify_jwt_token, oauth2_scheme, create_user_if_not_exists
from datetime import datetime


router = APIRouter()

ns_pkg = app.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.delete(
    "/users/{id}",
    responses={
        204: {"description": "User deleted"},
    },
    tags=["users"],
    summary="Delete user account",
    response_model_by_alias=True,
)
async def users_id_delete(
    id: StrictInt = Path(..., description=""),
) -> None:
    if not BaseUsers.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseUsers.subclasses[0]().users_id_delete(id)


@router.get(
    "/users",
    responses={
        200: {"model": List[User], "description": "List of users"},
    },
    tags=["users"],
    summary="List users (filtered by organization if org_id provided)",
    response_model_by_alias=True,
)
async def users_get(
    org_id: Optional[int] = Query(None, description="Filter by organization ID"),
    search: Optional[str] = Query(None, description="Search by username or display name"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
) -> List[User]:
    # Calculate offset
    offset = (page - 1) * limit
    
    # Start with base query using select() instead of query()
    query = select(UserModel)
    
    # Apply organization filter if provided
    if org_id is not None:
        # Check if current user has access to this organization
        if not any(m.organization_id == org_id for m in current_user.organization_memberships):
            raise HTTPException(status_code=403, detail="Access denied to this organization")
        
        # Use join and where instead of join and filter
        query = query.join(OrganizationMember).where(OrganizationMember.organization_id == org_id)
    
    # Apply search filter if provided
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                UserModel.username.ilike(search_term),
                UserModel.display_name.ilike(search_term),
                UserModel.email.ilike(search_term)
            )
        )
    
    # Get total count with proper async execution
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    
    # Apply ordering and pagination
    query = query.order_by(UserModel.username) \
                 .offset(offset) \
                 .limit(limit)
    
    # Execute the query asynchronously
    result = await db.execute(query)
    users = result.scalars().all()
    
    return [User.model_validate(user) for user in users]


@router.get(
    "/users/{id}",
    responses={
        200: {"model": User, "description": "User data"},
    },
    tags=["users"],
    summary="Get user by ID",
    response_model_by_alias=True,
)
async def users_id_get(
    id: StrictInt = Path(..., description="User ID"),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
) -> User:
    # Create a select statement instead of using db.query
    query = select(UserModel).where(UserModel.id == id)
    
    # Execute the query asynchronously
    result = await db.execute(query)
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if current user has access to view this user
    # Users can view themselves and users in their organizations
    if user.id != current_user.id:
        # Get organizations in common
        current_user_orgs = {m.organization_id for m in current_user.organization_memberships}
        target_user_orgs = {m.organization_id for m in user.organization_memberships}
        
        if not current_user_orgs.intersection(target_user_orgs):
            # Only show basic public info if no common organizations
            return User(
                id=user.id,
                username=user.username,
                display_name=user.display_name,
                picture_url=user.picture_url
            )
    
    return User.model_validate(user)


@router.patch(
    "/users/{id}",
    responses={
        200: {"model": User, "description": "User updated"},
    },
    tags=["users"],
    summary="Update user",
    response_model_by_alias=True,
)
async def users_id_patch(
    id: StrictInt = Path(..., description="User ID"),
    user_update_request: UserUpdateRequest = Body(None, description=""),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
) -> User:
    # Users can only update their own profile unless they're an admin
    if id != current_user.id and current_user.default_role != "admin":
        raise HTTPException(status_code=403, detail="Can only update your own profile")
    
    # Create a select statement
    query = select(UserModel).where(UserModel.id == id)
    
    # Execute query asynchronously
    result = await db.execute(query)
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields
    if user_update_request.email is not None:
        # Check email uniqueness
        existing_query = select(UserModel).where(
            UserModel.email == user_update_request.email,
            UserModel.id != id
        )
        existing_result = await db.execute(existing_query)
        existing = existing_result.scalars().first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Email already in use")
        user.email = user_update_request.email
        
    if user_update_request.display_name is not None:
        user.display_name = user_update_request.display_name
    
    user.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user)
    return User.model_validate(user)

@router.get(
    "/users/me",
    responses={
        200: {"model": User, "description": "Current user data"},
    },
    tags=["users"],
    summary="Get current user data",
    response_model_by_alias=True,
)
async def users_me_get(
    current_user: UserModel = Depends(get_current_user)
) -> User:
    return User.model_validate(current_user)

@router.patch(
    "/users/me",
    responses={
        200: {"model": User, "description": "Current user updated"},
    },
    tags=["users"],
    summary="Update current user",
    response_model_by_alias=True,
)
async def users_me_patch(
    user_update_request: UserUpdateRequest = Body(None, description=""),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
) -> User:
    # Update fields
    if user_update_request.email is not None:
        # Check email uniqueness
        existing = await db.execute(select(UserModel).filter(UserModel.email == user_update_request.email))
        if existing.scalars().first():
            raise HTTPException(status_code=400, detail="Email already in use")
        current_user.email = user_update_request.email
        
    if user_update_request.display_name is not None:
        current_user.display_name = user_update_request.display_name
    
    current_user.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(current_user)
    return User.model_validate(current_user)

@router.get(
    "/users/me/{id_token}",
    responses={
        200: {"model": User, "description": "Current user data"},
    },
    tags=["users"],
    summary="Create current user",
    response_model_by_alias=True,
)
async def users_me_create(
    id_token: str = Path(..., description="Auth0 ID token"),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(create_user_if_not_exists)
) -> User:
    user = await create_user_if_not_exists(id_token, db)
    return User.model_validate(user)
