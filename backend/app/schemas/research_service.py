from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from app.schemas._base_model import CustomBaseModel

class ResearchServiceBase(CustomBaseModel):
    """Base schema for research services"""
    service_key: str
    name: str
    description: Optional[str] = None
    url: Optional[str] = None
    default_model_id: Optional[int] = None

class ResearchServiceCreate(ResearchServiceBase):
    """Schema for creating a new research service"""
    pass

class ResearchService(ResearchServiceBase):
    """Schema for a complete research service"""
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    default_model: Optional["AiModelInResearchService"] = None
    # models: Optional[List["AiModelInResearchService"]] = None
    service_models: List["ResearchServiceModel"] = []

    model_config = ConfigDict(from_attributes=True)

# Avoid circular imports
from .ai_model import AiModelInResearchService
from .research_service_model import ResearchServiceModel 