# backend/app/routers/api_keys.py
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
import secrets

from app.db import get_db
from app.models import User, ApiKey
from app.schemas.api_key_create import ApiKeyCreate
from app.schemas.api_key_response import ApiKeyResponse
from app.services.authentication import get_current_user

router = APIRouter()

@router.post(
    "/api-keys",
    responses={
        200: {"model": ApiKeyResponse, "description": "API key created successfully"},
    },
    tags=["api-keys"],
    summary="Create new API key",
    response_model_by_alias=True,
)
async def create_api_key(
    api_key_data: ApiKeyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    org_id: Optional[int] = Query(None, description="Organization ID for the API key")
) -> ApiKeyResponse:
    """Create a new API key for the current user"""
    # Generate a secure random API key
    api_key = secrets.token_urlsafe(64)
    
    # Calculate expiration date
    expires_at = datetime.utcnow() + timedelta(days=api_key_data.expires_in_days)
    
    # Create new API key record
    db_api_key = ApiKey(
        token=api_key,
        name=api_key_data.name,
        user_id=current_user.id if not org_id else None,
        organization_id=org_id,
        expires_at=expires_at
    )
    
    await db.add(db_api_key)
    await db.commit()
    await db.refresh(db_api_key)
    
    # Convert datetime objects to ISO string format for Pydantic validation
    created_at_str = db_api_key.created_at.isoformat() if db_api_key.created_at else None
    expires_at_str = db_api_key.expires_at.isoformat() if db_api_key.expires_at else None
    
    return ApiKeyResponse(
        token=api_key,
        name=db_api_key.name,
        user_id=db_api_key.user_id,
        organization_id=db_api_key.organization_id,
        created_at=created_at_str,
        expires_at=expires_at_str,
        is_active=db_api_key.is_active
    )

@router.get(
    "/api-keys",
    responses={
        200: {"model": List[ApiKeyResponse], "description": "List of API keys"},
    },
    tags=["api-keys"],
    summary="List user API keys",
    response_model_by_alias=True,
)
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[ApiKeyResponse]:
    """List all API keys for the current user"""
    query = select(ApiKey).where(
        ApiKey.user_id == current_user.id
    )
    result = await db.execute(query)
    api_keys = result.scalars().all()
    
    return [ApiKeyResponse.model_validate(api_key) for api_key in api_keys]

@router.delete(
    "/api-keys/{key_id}",
    responses={
        200: {"description": "API key revoked successfully"},
    },
    tags=["api-keys"],
    summary="Revoke API key",
    response_model_by_alias=True,
)
async def revoke_api_key(
    key_id: int = Path(..., description="API key ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Revoke an API key"""
    stmt = select(ApiKey).where(
        ApiKey.id == key_id,
        ApiKey.user_id == current_user.id
    )
    result = await db.execute(stmt)
    api_key = result.scalars().first()
    
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    api_key.is_active = False
    await db.commit()
    
    return {"message": "API key revoked successfully"} 