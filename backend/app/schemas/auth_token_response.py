from __future__ import annotations
import pprint
import json
from pydantic import BaseModel, ConfigDict, StrictStr, StrictInt
from typing import Any, ClassVar, Dict, List
try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

class AuthTokenResponse(BaseModel):
    """
    AuthTokenResponse
    """
    access_token: StrictStr
    token_type: StrictStr
    expires_in: StrictInt
    refresh_token: StrictStr
    id_token: StrictStr
    
    __properties: ClassVar[List[str]] = ["access_token", "token_type", "expires_in", "refresh_token", "id_token"]

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "protected_namespaces": (),
    }

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of AuthTokenResponse from a JSON string"""
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
        """Create an instance of AuthTokenResponse from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "access_token": obj.get("access_token"),
            "token_type": obj.get("token_type"),
            "expires_in": obj.get("expires_in")
        })
        return _obj 