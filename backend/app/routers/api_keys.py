# backend/app/routers/api_keys.py
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
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
    db: Session = Depends(get_db),
    org_id: Optional[int] = Query(None, description="Organization ID for the API key")
) -> ApiKeyResponse:
    """Create a new API key for the current user"""
    # Generate a secure random API key
    api_key = secrets.token_urlsafe(64)
    
    # Calculate expiration date
    expires_at = datetime.utcnow() + timedelta(days=api_key_data.expires_in_days)
    
    # Create new API key record
    db_api_key = ApiKey(
        key=api_key,
        name=api_key_data.name,
        user_id=current_user.id,
        organization_id=org_id,
        expires_at=expires_at
    )
    
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    
    return ApiKeyResponse(
        key=api_key,
        name=db_api_key.name,
        created_at=db_api_key.created_at,
        expires_at=db_api_key.expires_at
    )

@router.get(
    "/api-keys",
    responses={
        200: {"model": list[ApiKeyResponse], "description": "List of API keys"},
    },
    tags=["api-keys"],
    summary="List user API keys",
    response_model_by_alias=True,
)
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> list[ApiKeyResponse]:
    """List all API keys for the current user"""
    return db.query(ApiKey).filter(
        ApiKey.user_id == current_user.id,
        ApiKey.is_active == True
    ).all()

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
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """Revoke an API key"""
    api_key = db.query(ApiKey).filter(
        ApiKey.id == key_id,
        ApiKey.user_id == current_user.id
    ).first()
    
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    api_key.is_active = False
    db.commit()
    
    return {"message": "API key revoked successfully"} 