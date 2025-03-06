# coding: utf-8

from typing import Dict, List, Optional  # noqa: F401
import importlib
import pkgutil

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

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, or_, and_, select, desc, asc
from sqlalchemy.orm import selectinload
from app.db import get_db
from app.models import DeepResearch as DeepResearchModel, ResearchRating, User
from app.schemas.extra_models import TokenModel  # noqa: F401
from pydantic import StrictInt
from typing import Any, List
from app.schemas.deep_research import DeepResearch
from app.schemas.deep_research_create_request import DeepResearchCreateRequest
from app.schemas.deep_research_update_request import DeepResearchUpdateRequest
from app.schemas.tag import Tag
from app.models import Tag as TagModel, DeepResearchTag
from app.services.authentication import get_current_user
from datetime import datetime

router = APIRouter()

ns_pkg = app.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


def get_deep_research_options():
    """
    Returns SQLAlchemy options to load all DeepResearch relationships.
    Used to consistently load relationships across all endpoints.
    """
    return [
        selectinload(DeepResearchModel.chunks),
        selectinload(DeepResearchModel.summaries),
        selectinload(DeepResearchModel.sources),
        selectinload(DeepResearchModel.auto_metadata),
        selectinload(DeepResearchModel.comments),
        selectinload(DeepResearchModel.ratings),
        selectinload(DeepResearchModel.research_job),
    ]


@router.get(
    "/deep-research",
    responses={
        200: {"model": List[DeepResearch], "description": "A list of deep research items"},
    },
    tags=["deep-research"],
    summary="List deep research items accessible to the user",
    response_model_by_alias=True,
)
async def research_get(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    visibility: Optional[str] = None,
    org_id: Optional[int] = None,
    order_by: Optional[str] = None,
    order: Optional[str] = "desc",
    creator_username: Optional[str] = None,
    model_name: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
) -> List[DeepResearch]:
    # Calculate offset
    offset = (page - 1) * limit
    
    # Build base query with avg_rating calculation and username
    query = (
        select(
            DeepResearchModel,
            func.coalesce(func.avg(ResearchRating.rating_value), 0.0).label('avg_rating'),
            User.username.label('creator_username')
        )
        .join(User, DeepResearchModel.user_id == User.id)
        .outerjoin(ResearchRating)
        .group_by(DeepResearchModel.id, User.username)
    )
    
    # Add visibility filters
    query = query.where(
        or_(
            DeepResearchModel.visibility == "public",
            DeepResearchModel.user_id == current_user.id,
            and_(
                DeepResearchModel.visibility == "org",
                DeepResearchModel.owner_org_id.isnot(None),
                DeepResearchModel.owner_org_id.in_([
                    m.organization_id for m in current_user.organization_memberships
                ])
            )
        )
    )

    # Add org filter if specified
    if org_id is not None:
        query = query.where(DeepResearchModel.owner_org_id == org_id)
    elif visibility: # Add visibility filter if specified
        query = query.where(DeepResearchModel.visibility == visibility)

    # Add creator_username filter if specified
    if creator_username:
        query = query.where(User.username.ilike(f"%{creator_username}%"))

    # Add model_name filter if specified
    if model_name:
        query = query.where(DeepResearchModel.model_name.ilike(f"%{model_name}%"))

    # Add sorting
    if order_by == 'avg_rating':
        sort_col = func.avg(ResearchRating.rating_value)
    else:
        sort_col = getattr(DeepResearchModel, order_by or 'created_at')
    
    query = query.order_by(desc(sort_col) if order == 'desc' else asc(sort_col))
    
    # Apply pagination and load relationships
    query = query.options(*get_deep_research_options()) \
                .offset(offset) \
                .limit(limit)
    
    # Execute query
    result = await db.execute(query)
    items = []
    for item, avg_rating, creator_username in result:
        # Convert to dict to add computed fields
        item_dict = DeepResearch.model_validate(item).model_dump()
        item_dict['avg_rating'] = float(avg_rating) if avg_rating is not None else None
        item_dict['creator_username'] = creator_username
        items.append(item_dict)
    
    return [DeepResearch.model_validate(item) for item in items]


@router.delete(
    "/deep-research/{id}",
    responses={
        204: {"description": "Research item deleted"},
    },
    tags=["deep-research"],
    summary="Delete a deep research item",
    response_model_by_alias=True,
)
async def research_id_delete(
    id: StrictInt = Path(..., description=""),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
) -> None:
    # Lookup the research item
    stmt = select(DeepResearchModel).where(DeepResearchModel.id == id)
    result = await db.execute(stmt)
    research = result.scalars().first()
    
    if not research:
        raise HTTPException(status_code=404, detail="Research item not found")
    
    # Check permissions
    if research.user_id != current_user.id:
        # Check if user is org admin for org-owned items
        if research.owner_org_id:
            org_member = next((m for m in current_user.organization_memberships 
                             if m.organization_id == research.owner_org_id), None)
            if not org_member or org_member.role not in ["admin", "owner"]:
                raise HTTPException(status_code=403, detail="Insufficient permissions to delete this research item")
        else:
            raise HTTPException(status_code=403, detail="Cannot delete another user's research item")
    
    await db.delete(research)
    await db.commit()
    return Response(status_code=204)

@router.get(
    "/deep-research/{id}",
    responses={
        200: {"model": DeepResearch, "description": "Research item data"},
    },
    tags=["deep-research"],
    summary="Retrieve a single deep research item",
    response_model_by_alias=True,
)
async def research_id_get(
    id: StrictInt = Path(..., description=""),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
) -> DeepResearch:
    # Lookup the research item with all relationships loaded
    stmt = select(DeepResearchModel).where(DeepResearchModel.id == id).options(*get_deep_research_options())
    result = await db.execute(stmt)
    research = result.scalars().first()
    
    if not research:
        raise HTTPException(status_code=404, detail="Research item not found")
    
    # Check access permissions
    if research.visibility != "public":
        if research.visibility == "private" and research.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        elif research.visibility == "org":
            org_member = next((m for m in current_user.organization_memberships 
                             if m.organization_id == research.owner_org_id), None)
            if not org_member:
                raise HTTPException(status_code=403, detail="Access denied")
    
    return DeepResearch.model_validate(research)

@router.patch(
    "/deep-research/{id}",
    responses={
        200: {"model": DeepResearch, "description": "Research item updated"},
    },
    tags=["deep-research"],
    summary="Update a deep research item",
    response_model_by_alias=True,
)
async def research_id_patch(
    id: StrictInt = Path(..., description=""),
    deep_research_update_request: DeepResearchUpdateRequest = Body(None, description=""),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
) -> DeepResearch:
    # Lookup the research item
    stmt = select(DeepResearchModel).where(DeepResearchModel.id == id)
    result = await db.execute(stmt)
    research = result.scalars().first()
    
    if not research:
        raise HTTPException(status_code=404, detail="Research item not found")
    
    # Check permissions
    if research.user_id != current_user.id:
        # Check if user is org admin for org-owned items
        if research.owner_org_id:
            org_member = next((m for m in current_user.organization_memberships 
                             if m.organization_id == research.owner_org_id), None)
            if not org_member or org_member.role not in ["admin", "owner"]:
                raise HTTPException(status_code=403, detail="Insufficient permissions to update this research item")
        else:
            raise HTTPException(status_code=403, detail="Cannot update another user's research item")
    
    # Update fields
    if deep_research_update_request.title is not None:
        research.title = deep_research_update_request.title
    if deep_research_update_request.final_report is not None:
        research.final_report = deep_research_update_request.final_report
    if deep_research_update_request.visibility is not None:
        # Validate visibility change for org items
        if deep_research_update_request.visibility == "org" and not research.owner_org_id:
            raise HTTPException(status_code=400, detail="Cannot set org visibility without an owner organization")
        research.visibility = deep_research_update_request.visibility
    
    # Save changes
    await db.commit()
    # Refresh the object with relationships loaded
    await db.refresh(research, options=get_deep_research_options())
    
    return DeepResearch.model_validate(research)

@router.post(
    "/deep-research",
    responses={
        201: {"model": DeepResearch, "description": "Deep research item created"},
    },
    tags=["deep-research"],
    summary="Create a new deep research item",
    response_model_by_alias=True,
)
async def research_post(
    deep_research_create_request: DeepResearchCreateRequest = Body(None, description=""),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
) -> DeepResearch:
    # Validate required fields
    if not all([
        deep_research_create_request.title,
        deep_research_create_request.prompt_text,
        deep_research_create_request.final_report,
        deep_research_create_request.visibility
    ]):
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    # Validate visibility
    if deep_research_create_request.visibility == "org":
        # Check if user belongs to any organization
        if not current_user.organization_memberships:
            raise HTTPException(status_code=400, detail="Cannot create org-visible item without organization membership")
        # Use the first organization the user is a member of
        owner_org_id = current_user.organization_memberships[0].organization_id
    else:
        owner_org_id = None
    
    # Create research item
    # TODO: add embeddings to the research item
    research = DeepResearchModel(
        user_id=current_user.id,
        owner_user_id=current_user.id,
        owner_org_id=owner_org_id,
        title=deep_research_create_request.title,
        prompt_text=deep_research_create_request.prompt_text,
        final_report=deep_research_create_request.final_report,
        visibility=deep_research_create_request.visibility,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Save to database
    db.add(research)
    await db.commit()
    # Refresh the object with relationships loaded
    await db.refresh(research, options=get_deep_research_options())
    
    return DeepResearch.model_validate(research)

@router.get(
    "/deep-research/{id}/tags",
    responses={
        200: {"model": List[Tag], "description": "Tags associated with the deep research item"},
    },
    tags=["deep-research"],
    summary="Get tags for a deep research item",
    response_model_by_alias=True,
)
async def research_id_tags_get(
    id: StrictInt = Path(..., description=""),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
) -> List[Tag]:
    # Lookup the research item first
    stmt = select(DeepResearchModel).where(DeepResearchModel.id == id)
    result = await db.execute(stmt)
    research = result.scalars().first()
    
    if not research:
        raise HTTPException(status_code=404, detail="Research item not found")
    
    # Check access permissions (same logic as in research_id_get)
    if research.visibility != "public":
        if research.visibility == "private" and research.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        elif research.visibility == "org":
            org_member = next((m for m in current_user.organization_memberships 
                             if m.organization_id == research.owner_org_id), None)
            if not org_member:
                raise HTTPException(status_code=403, detail="Access denied")
    
    # Query tags associated with this research item
    query = select(TagModel).join(
        DeepResearchTag, 
        TagModel.id == DeepResearchTag.tag_id
    ).where(
        DeepResearchTag.deep_research_id == id
    )
    
    tag_result = await db.execute(query)
    tags = tag_result.scalars().all()
    
    return [Tag.model_validate(tag) for tag in tags]
