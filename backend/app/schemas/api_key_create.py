from __future__ import annotations
import pprint
import json
from pydantic import BaseModel, ConfigDict, StrictStr, StrictInt
from typing import Any, ClassVar, Dict, List, Optional
try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

from app.schemas._base_model import CustomBaseModel

class ApiKeyCreate(CustomBaseModel):
    """
    ApiKeyCreate
    """
    name: StrictStr
    api_service_name: Optional[StrictStr] = "DRKR"
    token: Optional[StrictStr] = None
    expires_in_days: Optional[StrictInt] = 365  # Default to 1 year

    __properties: ClassVar[List[str]] = ["name", "api_service_name", "token", "expires_in_days"]

    model_config = {
        "populate_by_name": True,
        "validate_assignment": False,
        "protected_namespaces": (),
    }

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))
 