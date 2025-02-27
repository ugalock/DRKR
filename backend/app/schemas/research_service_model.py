from pydantic import BaseModel, ConfigDict

class ResearchServiceModelBase(BaseModel):
    """Base schema for research service model relationships"""
    service_id: int
    model_id: int
    is_default: bool = False

class ResearchServiceModelCreate(ResearchServiceModelBase):
    """Schema for creating a new research service model relationship"""
    pass

class ResearchServiceModel(ResearchServiceModelBase):
    """Schema for a complete research service model relationship"""
    id: int
    created_at: str
    updated_at: str
    model: "AiModelInResearchService"

    model_config = ConfigDict(from_attributes=True)

# Avoid circular imports
from .ai_model import AiModelInResearchService 