from __future__ import annotations
import pprint
import json
from pydantic import BaseModel, ConfigDict, StrictStr, StrictInt
from typing import Any, ClassVar, Dict, List
try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

from app.schemas._base_model import CustomBaseModel

class AuthTokenResponse(CustomBaseModel):
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
        "validate_assignment": False,
        "protected_namespaces": (),
    }

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))
 