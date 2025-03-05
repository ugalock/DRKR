from __future__ import annotations
import pprint
import json

from pydantic import BaseModel, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

from app.schemas._base_model import CustomBaseModel

class ResearchChunk(CustomBaseModel):
    """
    ResearchChunk
    """
    id: StrictInt
    deep_research_id: StrictInt
    chunk_index: StrictInt
    chunk_type: Optional[StrictStr] = None
    chunk_text: StrictStr
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    __properties: ClassVar[List[str]] = ["id", "deep_research_id", "chunk_index", "chunk_type", "chunk_text", "created_at", "updated_at"]

    model_config = {
        "populate_by_name": True,
        "validate_assignment": False,
        "protected_namespaces": (),
        "from_attributes": True,
    }

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))
 