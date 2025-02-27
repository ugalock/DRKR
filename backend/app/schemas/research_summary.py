from __future__ import annotations
import pprint
import json

from pydantic import BaseModel, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

class ResearchSummary(BaseModel):
    """
    ResearchSummary
    """
    id: StrictInt
    deep_research_id: StrictInt
    summary_scope: StrictStr
    summary_length: StrictStr
    summary_text: StrictStr
    created_at: Optional[StrictStr] = None
    __properties: ClassVar[List[str]] = ["id", "deep_research_id", "summary_scope", "summary_length", "summary_text", "created_at"]

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
        """Create an instance of ResearchSummary from a JSON string"""
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
        """Create an instance of ResearchSummary from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "deep_research_id": obj.get("deep_research_id"),
            "summary_scope": obj.get("summary_scope"),
            "summary_length": obj.get("summary_length"),
            "summary_text": obj.get("summary_text"),
            "created_at": obj.get("created_at"),
        })
        return _obj 