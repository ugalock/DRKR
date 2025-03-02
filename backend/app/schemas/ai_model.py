from pydantic import BaseModel, ConfigDict
from typing import Dict, Optional

class AiModelBase(BaseModel):
    """Base schema for AI models"""
    model_key: str
    default_params: Dict
    max_tokens: int
    is_active: bool = True

class AiModelCreate(AiModelBase):
    """Schema for creating a new AI model"""
    pass

class AiModelInResearchService(AiModelBase):
    """Schema for AI model when included in a research service"""
    id: int
    is_default: bool = False

    model_config = ConfigDict(from_attributes=True)

class AiModel(AiModelBase):
    """Schema for a complete AI model"""
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
