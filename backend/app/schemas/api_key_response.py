from __future__ import annotations
import pprint
import json
from pydantic import BaseModel, StrictStr, StrictInt, StrictBool
from typing import Any, ClassVar, Dict, List, Optional
try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

class ApiKeyResponse(BaseModel):
    """
    ApiKeyResponse
    """
    token: StrictStr
    name: StrictStr
    user_id: Optional[StrictInt] = None
    organization_id: Optional[StrictInt] = None
    created_at: StrictStr
    expires_at: StrictStr
    is_active: Optional[StrictBool] = True
    __properties: ClassVar[List[str]] = ["token", "name", "user_id", "organization_id", "is_active", "created_at", "expires_at"]

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "protected_namespaces": (),
        "from_attributes": True
    }

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of ApiKeyResponse from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias"""
        _dict = self.model_dump(
            by_alias=True,
            exclude={},
            exclude_none=True,
        )
        return _dict

    @classmethod
    def from_dict(cls, obj: Dict) -> Self:
        """Create an instance of ApiKeyResponse from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "token": obj.get("token"),
            "name": obj.get("name"),
            "user_id": obj.get("user_id"),
            "organization_id": obj.get("organization_id"),
            "is_active": obj.get("is_active"),
            "created_at": obj.get("created_at"),
            "expires_at": obj.get("expires_at")
        })
        return _obj 