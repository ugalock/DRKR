# coding: utf-8

from typing import Dict, List, Optional
import importlib
import pkgutil

from app.routers.research_jobs_base import BaseResearchJobs
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
from pydantic import StrictStr
from app.schemas.research_job import ResearchJob
from app.schemas.research_job_create_request import ResearchJobCreateRequest
from app.schemas.research_job_create_response import ResearchJobCreateResponse
from app.schemas.research_job_update_request import ResearchJobUpdateRequest
from app.schemas.research_job_get_request import ResearchJobGetRequest
from app.schemas.research_job_answer_request import ResearchJobAnswerRequest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, desc, asc

from app.services.authentication import get_current_user
from app.db import get_db
from app.models import User, ResearchJob as ResearchJobModel
from app.schemas.research_job import ResearchJob as ResearchJobSchema
from app.services.research import ResearchService

router = APIRouter()
research_service = ResearchService()

ns_pkg = app.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)

def check_research_job_permissions(job: ResearchJobModel, current_user: User) -> bool:
    """Check if current user has permission to access the research job."""
    # Direct owner
    if job.user_id == current_user.id:
        return True
        
    # Check visibility permissions
    if job.visibility == "private":
        return False
    elif job.visibility == "public":
        return True
    elif job.visibility == "org":
        return (job.owner_org_id is not None and 
                job.owner_org_id in [m.organization_id for m in current_user.organization_memberships])
    
    return False

@router.get(
    "/research-jobs",
    response_model=List[ResearchJobSchema],
    responses={
        200: {"description": "List of research jobs"},
        401: {"description": "Not authenticated"},
    },
    tags=["research-jobs"],
    summary="List all research jobs",
)
async def research_jobs_get(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    service: Optional[str] = None,
    status: Optional[str] = None,
    visibility: Optional[str] = None,
    org_id: Optional[int] = None,
    order_by: Optional[str] = None,
    order: Optional[str] = "desc",
    model_name: Optional[str] = None,
) -> List[ResearchJobSchema]:
    """List research jobs with optional filtering."""
    # Calculate offset
    offset = (page - 1) * limit
    
    # Build base query with username
    query = (
        select(ResearchJobModel)
        .join(User, ResearchJobModel.user_id == User.id)
    )
    
    # Add visibility filters
    query = query.where(
        or_(
            ResearchJobModel.visibility == "public",
            ResearchJobModel.user_id == current_user.id,
            and_(
                ResearchJobModel.visibility == "org",
                ResearchJobModel.owner_org_id.isnot(None),
                ResearchJobModel.owner_org_id.in_([
                    m.organization_id for m in current_user.organization_memberships
                ])
            )
        )
    )

    # Add filters
    if service:
        query = query.where(ResearchJobModel.service.ilike(f"%{service}%"))
    if status:
        query = query.where(ResearchJobModel.status == status)
    if org_id is not None:
        query = query.where(ResearchJobModel.owner_org_id == org_id)
    elif visibility:
        query = query.where(ResearchJobModel.visibility == visibility)
    if model_name:
        query = query.where(ResearchJobModel.model_name.ilike(f"%{model_name}%"))

    # Add sorting
    sort_col = getattr(ResearchJobModel, order_by or 'created_at')
    query = query.order_by(desc(sort_col) if order == 'desc' else asc(sort_col))
    
    # Apply pagination
    query = query.offset(offset).limit(limit)
    
    # Execute query
    result = await db.execute(query)
    jobs = result.scalars().all()
    
    # Filter for permissions and convert to schema
    return [ResearchJobSchema.model_validate(job) for job in jobs if check_research_job_permissions(job, current_user)]

@router.post(
    "/research-jobs/get",
    response_model=ResearchJobSchema,
    responses={
        200: {"description": "Research job retrieval by id or (job_id, service)"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized"},
        404: {"description": "Research job not found"},
    },
    tags=["research-jobs"],
    summary="Retrieve a background research job and potentially poll its status",
)
async def research_jobs_get(
    request: ResearchJobGetRequest = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResearchJobSchema:
    id = request.id if hasattr(request, 'id') else None
    job_id = request.job_id if hasattr(request, 'job_id') else None
    service = request.service if hasattr(request, 'service') else None
    if not id and (not job_id or not service):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either id or job_id and service must be provided"
        )
    """Get research job status."""
    result = await research_service.poll_status(
        db=db,
        user_id=current_user.id,
        id=id,
        job_id=job_id,
        service=service
    )
    
    if not check_research_job_permissions(result["job"], current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this research job"
        )
    
    return result["job"]

@router.patch(
    "/research-jobs/{id}",
    response_model=ResearchJobSchema,
    responses={
        200: {"description": "Research job update by id"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized"},
        404: {"description": "Research job not found"},
    },
    tags=["research-jobs"],
    summary="Update a background research job",
)
async def research_jobs_id_patch(
    id: int = Path(...),
    request: ResearchJobUpdateRequest = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResearchJobSchema:
    """Update research job."""
    # Get existing job
    stmt = select(ResearchJobModel).where(ResearchJobModel.id == id)
    db_job = await db.execute(stmt)
    db_job = db_job.scalar_one_or_none()
    
    if not db_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research job not found"
        )
    
    # Check ownership (only owner can update)
    if db_job.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the job owner can update the job"
        )
    
    # Handle status update to cancelled
    if request.status == "cancelled":
        if db_job.status not in ["failed", "complete", "cancelled"]:
            return await research_service.cancel_job(
                db=db,
                service=db_job.service,
                user_id=current_user.id,
                job_id=db_job.job_id
            )
        return ResearchJobSchema.model_validate(db_job)
    
    # Update other fields
    if request.visibility:
        db_job.visibility = request.visibility
    
    await db.commit()
    await db.refresh(db_job)
    
    return ResearchJobSchema.model_validate(db_job)

@router.post(
    "/research-jobs",
    response_model=ResearchJobCreateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Research job started"},
        401: {"description": "Not authenticated"},
        400: {"description": "Invalid request"},
    },
    tags=["research-jobs"],
    summary="Launch a new background research job",
)
async def research_jobs_post(
    request: ResearchJobCreateRequest = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResearchJobCreateResponse:
    """Start a new research job."""
    result = await research_service.start_job(
        db=db,
        service=request.service,
        user_id=str(current_user.id),
        prompt=request.prompt,
        model=request.model,
        model_params=request.model_params,
        visibility=request.visibility,
        org_id=request.org_id
    )
    return result

@router.post(
    "/research-jobs/answer",
    response_model=ResearchJobSchema,
    responses={
        200: {"description": "Answers submitted successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized"},
        404: {"description": "Research job not found"},
    },
    tags=["research-jobs"],
    summary="Submit answers to research job follow-up questions",
)
async def research_jobs_answer(
    request: ResearchJobAnswerRequest = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResearchJobSchema:
    """Submit answers to follow-up questions."""
    return await research_service.answer_questions(
        db=db,
        service=request.service,
        user_id=current_user.id,
        job_id=request.job_id,
        answers=request.answers
    )
