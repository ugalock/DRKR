# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil
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
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, or_, union_all, and_
from pydantic import StrictInt
from typing import Any, List

import app.impl
from app.db import get_db
from app.models import Tag as TagModel, DeepResearch, DeepResearchTag
from app.schemas.extra_models import TokenModel  # noqa: F401
from app.schemas.deep_research import DeepResearch
from app.schemas.tag import Tag
from app.schemas.tag_create_request import TagCreateRequest
from app.schemas.tag_update_request import TagUpdateRequest
from app.services.authentication import get_current_user

router = APIRouter()

ns_pkg = app.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/tags",
    responses={
        200: {"model": List[Tag], "description": "List of tags"},
    },
    tags=["tags"],
    summary="List all tags (global, org, or user-specific) accessible to the user",
    response_model_by_alias=True,
)
async def tags_get(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
) -> List[Tag]:
    # Get global tags
    global_tags_stmt = select(TagModel).where(TagModel.is_global == True)
    
    # User-specific tags
    user_tags_stmt = select(TagModel).where(TagModel.user_id == current_user.id)
    
    # Union of global and user tags
    combined_stmt = global_tags_stmt.union(user_tags_stmt)
    
    # Add organization-specific tags if user is in any organizations
    org_ids = [membership.organization_id for membership in current_user.organization_memberships]
    if org_ids:
        org_tags_stmt = select(TagModel).where(TagModel.organization_id.in_(org_ids))
        combined_stmt = combined_stmt.union(org_tags_stmt)
    
    # Add ordering
    combined_stmt = combined_stmt.order_by(TagModel.name)
    
    # Execute the query
    result = await db.execute(combined_stmt)
    tags = result.scalars().all()
    
    return [Tag.model_validate(tag) for tag in tags]

@router.delete(
    "/tags/{id}",
    responses={
        204: {"description": "Tag removed"},
    },
    tags=["tags"],
    summary="Delete a tag",
    response_model_by_alias=True,
)
async def tags_id_delete(
    id: StrictInt = Path(..., description=""),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
) -> None:
    # Get the tag
    stmt = select(TagModel).where(TagModel.id == id)
    result = await db.execute(stmt)
    tag = result.scalars().first()
    
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    # Check permissions
    if tag.is_global:
        # Only admins can delete global tags
        if current_user.default_role != "admin":
            raise HTTPException(status_code=403, detail="Only admins can delete global tags")
    elif tag.user_id:
        # Users can only delete their own tags
        if tag.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Cannot delete another user's tag")
    else:
        # For org tags, check if user is org admin
        org_member = next((m for m in current_user.organization_memberships 
                          if m.organization_id == tag.organization_id), None)
        if not org_member or org_member.role not in ["admin", "owner"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions to delete organization tag")
    
    await db.delete(tag)
    await db.commit()
    return Response(status_code=204)

@router.get(
    "/tags/{id}",
    responses={
        200: {"model": Tag, "description": "Tag data"},
    },
    tags=["tags"],
    summary="Retrieve a specific tag",
    response_model_by_alias=True,
)
async def tags_id_get(
    id: StrictInt = Path(..., description=""),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Tag:
    # Get the tag
    stmt = select(TagModel).where(TagModel.id == id)
    result = await db.execute(stmt)
    tag = result.scalars().first()
    
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    # Check if user has access to this tag
    if not tag.is_global:
        if tag.user_id and tag.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        if tag.organization_id:
            org_member = next((m for m in current_user.organization_memberships 
                             if m.organization_id == tag.organization_id), None)
            if not org_member:
                raise HTTPException(status_code=403, detail="Access denied")
    
    return Tag.model_validate(tag)

@router.patch(
    "/tags/{id}",
    responses={
        200: {"model": Tag, "description": "Tag updated"},
    },
    tags=["tags"],
    summary="Update an existing tag",
    response_model_by_alias=True,
)
async def tags_id_patch(
    id: StrictInt = Path(..., description=""),
    tag_update_request: TagUpdateRequest = Body(None, description=""),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Tag:
    # Get the tag
    query = select(TagModel).where(TagModel.id == id)
    result = await db.execute(query)
    tag = result.scalars().first()
    
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    # Check permissions similar to delete
    if tag.is_global:
        if current_user.default_role != "admin":
            raise HTTPException(status_code=403, detail="Only admins can modify global tags")
    elif tag.user_id:
        if tag.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Cannot modify another user's tag")
    else:
        org_member = next((m for m in current_user.organization_memberships 
                          if m.organization_id == tag.organization_id), None)
        if not org_member or org_member.role not in ["admin", "owner"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions to modify organization tag")
    
    # Update fields
    if tag_update_request.name is not None:
        # Check name uniqueness in the appropriate scope
        name_exists = False
        if tag.is_global:
            global_query = select(TagModel).where(
                TagModel.is_global == True,
                func.lower(TagModel.name) == func.lower(tag_update_request.name),
                TagModel.id != id
            )
            global_result = await db.execute(global_query)
            name_exists = global_result.scalars().first() is not None
        elif tag.organization_id:
            org_query = select(TagModel).where(
                TagModel.organization_id == tag.organization_id,
                func.lower(TagModel.name) == func.lower(tag_update_request.name),
                TagModel.id != id
            )
            org_result = await db.execute(org_query)
            name_exists = org_result.scalars().first() is not None
        else:
            user_query = select(TagModel).where(
                TagModel.user_id == tag.user_id,
                func.lower(TagModel.name) == func.lower(tag_update_request.name),
                TagModel.id != id
            )
            user_result = await db.execute(user_query)
            name_exists = user_result.scalars().first() is not None
            
        if name_exists:
            raise HTTPException(status_code=400, detail="Tag name already exists in this scope")
        tag.name = tag_update_request.name
        
    if tag_update_request.description is not None:
        tag.description = tag_update_request.description
    
    await db.commit()
    await db.refresh(tag)
    return Tag.model_validate(tag)

@router.get(
    "/tags/{id}/research",
    responses={
        200: {"model": List[DeepResearch], "description": "List of research items"},
    },
    tags=["tags"],
    summary="List research items associated with a particular tag",
    response_model_by_alias=True,
)
async def tags_id_research_get(
    id: StrictInt = Path(..., description=""),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
) -> List[DeepResearch]:
    # Get the tag
    tag_query = select(TagModel).where(TagModel.id == id)
    tag_result = await db.execute(tag_query)
    tag = tag_result.scalars().first()
    
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    # Check if user has access to this tag
    if not tag.is_global:
        if tag.user_id and tag.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        if tag.organization_id:
            org_member = next((m for m in current_user.organization_memberships 
                             if m.organization_id == tag.organization_id), None)
            if not org_member:
                raise HTTPException(status_code=403, detail="Access denied")
    
    # Get research items with this tag that the user has access to
    research_query = (
        select(DeepResearch)
        .join(DeepResearchTag)
        .where(DeepResearchTag.tag_id == id)
        .where(
            or_(
                DeepResearch.visibility == "public",
                DeepResearch.user_id == current_user.id,
                and_(
                    DeepResearch.visibility == "org",
                    DeepResearch.owner_org_id.in_([m.organization_id for m in current_user.organization_memberships])
                )
            )
        )
        .order_by(DeepResearch.created_at.desc())
    )
    
    # Execute the query asynchronously
    research_result = await db.execute(research_query)
    research_items = research_result.scalars().all()
    
    return [DeepResearch.model_validate(item) for item in research_items]

@router.post(
    "/tags",
    responses={
        201: {"model": Tag, "description": "Tag created"},
    },
    tags=["tags"],
    summary="Create a new tag",
    response_model_by_alias=True,
)
async def tags_post(
    tag_create_request: TagCreateRequest = Body(None, description=""),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Tag:
    # Check if user can create the requested tag type
    if tag_create_request.is_global:
        if current_user.default_role != "admin":
            raise HTTPException(status_code=403, detail="Only admins can create global tags")
    elif tag_create_request.organization_id:
        org_member = next((m for m in current_user.organization_memberships 
                          if m.organization_id == tag_create_request.organization_id), None)
        if not org_member or org_member.role not in ["admin", "owner"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions to create organization tags")
    
    # Check name uniqueness in the appropriate scope
    name_exists = False
    if tag_create_request.is_global:
        global_query = select(TagModel).where(
            TagModel.is_global == True,
            func.lower(TagModel.name) == func.lower(tag_create_request.name)
        )
        global_result = await db.execute(global_query)
        name_exists = global_result.scalars().first() is not None
    elif tag_create_request.organization_id:
        org_query = select(TagModel).where(
            TagModel.organization_id == tag_create_request.organization_id,
            func.lower(TagModel.name) == func.lower(tag_create_request.name)
        )
        org_result = await db.execute(org_query)
        name_exists = org_result.scalars().first() is not None
    else:
        user_query = select(TagModel).where(
            TagModel.user_id == current_user.id,
            func.lower(TagModel.name) == func.lower(tag_create_request.name)
        )
        user_result = await db.execute(user_query)
        name_exists = user_result.scalars().first() is not None
        
    if name_exists:
        raise HTTPException(status_code=400, detail="Tag name already exists in this scope")
    
    # Create the tag
    tag = TagModel(
        name=tag_create_request.name,
        description=tag_create_request.description,
        is_global=tag_create_request.is_global,
        organization_id=tag_create_request.organization_id if not tag_create_request.is_global else None,
        user_id=current_user.id if not (tag_create_request.is_global or tag_create_request.organization_id) else None
    )
    
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    
    return Tag.model_validate(tag)