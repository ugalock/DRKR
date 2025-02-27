from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.schemas.research_service import ResearchService as ResearchServiceSchema
from app.services.authentication import get_current_user
from app.services.research import ResearchService
from app.models import User

research_service = ResearchService()

router = APIRouter(
    prefix="/research-services",
    tags=["research-services"]
)

@router.get("", response_model=List[ResearchServiceSchema])
async def list_research_services(
    service: Optional[str] = Query(None, description="Filter by service key"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[ResearchServiceSchema]:
    """
    Get all research services or filter by service key.
    
    Args:
        service: Optional service key to filter by
        db: Database session injected by FastAPI
        
    Returns:
        List of research services
    """
    services = await research_service.get_research_services(db, service_key=service)
    return [ResearchServiceSchema.model_validate(svc) for svc in services] 