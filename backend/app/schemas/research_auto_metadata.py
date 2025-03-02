from __future__ import annotations
import pprint
import json

from pydantic import BaseModel, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

class ResearchAutoMetadata(BaseModel):
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
        "validate_assignment": True,
        "protected_namespaces": (),
        "from_attributes": True,
    }

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of ResearchAutoMetadata from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        _dict = self.model_dump(
            by_alias=True,
            exclude={
            },
            exclude_none=True,
        )
        return _dict

    @classmethod
    def from_dict(cls, obj: Dict) -> Self:
        """Create an instance of ResearchAutoMetadata from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "deep_research_id": obj.get("deep_research_id"),
            "meta_key": obj.get("meta_key"),
            "meta_value": obj.get("meta_value"),
            "confidence_score": obj.get("confidence_score"),
            "created_at": obj.get("created_at"),
        })
        return _obj 