# backend/app/routers/api_keys.py
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
import secrets

from app.db import get_db
from app.models import User, ApiKey, ApiService
from app.schemas.api_key_create import ApiKeyCreate
from app.schemas.api_key import ApiKey
from app.services.authentication import get_current_user

router = APIRouter()

@router.post(
    "/api-keys",
    responses={
        200: {"model": ApiKey, "description": "API key created successfully"},
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
) -> ApiKey:
    """Create a new API key for the current user"""
    # Get the API service ID based on the provided name
    api_service = await db.execute(
        select(ApiService).where(ApiService.name == api_key_data.api_service_name)
    )
    api_service = api_service.scalar_one_or_none()
    if not api_service:
        raise HTTPException(status_code=404, detail="API service not found")
    
    # Generate a secure random API key
    api_key = api_key_data.token if (api_key_data.token and api_key_data.api_service_name != "DRKR") else secrets.token_urlsafe(64)
    
    # Calculate expiration date
    expires_at = datetime.utcnow() + timedelta(days=api_key_data.expires_in_days)
    
    # Create new API key record
    db_api_key = ApiKey(
        api_service_id=api_service.id,
        token=api_key,
        name=api_key_data.name,
        user_id=current_user.id if not org_id else None,
        organization_id=org_id,
        expires_at=expires_at
    )
    
    db.add(db_api_key)
    await db.commit()
    await db.refresh(db_api_key)
    
    _ = db_api_key.api_service # This will trigger the lazy loading
    
    return ApiKey.model_validate(db_api_key)

@router.get(
    "/api-keys",
    responses={
        200: {"model": List[ApiKey], "description": "List of API keys"},
    },
    tags=["api-keys"],
    summary="List user API keys",
    response_model_by_alias=True,
)
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[ApiKey]:
    """List all API keys for the current user"""
    query = select(ApiKey).where(
        ApiKey.user_id == current_user.id
    ).options(selectinload(ApiKey.api_service))
    result = await db.execute(query)
    api_keys = result.scalars().all()
    
    return [ApiKey.model_validate(api_key) for api_key in api_keys]

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