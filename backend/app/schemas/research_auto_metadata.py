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

class ResearchAutoMetadata(CustomBaseModel):
    """
    ResearchAutoMetadata
    """
    id: StrictInt
    deep_research_id: StrictInt
    meta_key: StrictStr
    meta_value: StrictStr
    confidence_score: Optional[StrictInt] = None
    created_at: Optional[str] = None
    __properties: ClassVar[List[str]] = ["id", "deep_research_id", "meta_key", "meta_value", "confidence_score", "created_at"]

    model_config = {
        "populate_by_name": True,
        "validate_assignment": False,
        "protected_namespaces": (),
        "from_attributes": True,
    }

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))
 