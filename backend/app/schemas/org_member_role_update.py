# coding: utf-8

from __future__ import annotations
import pprint
import re
import json

from pydantic import BaseModel, ConfigDict, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

from app.schemas._base_model import CustomBaseModel

class OrgMemberRoleUpdate(CustomBaseModel):
    """
    OrgMemberRoleUpdate
    """
    role: StrictStr
    __properties: ClassVar[List[str]] = ["role"]

    model_config = {
        "populate_by_name": True,
        "validate_assignment": False,
        "protected_namespaces": (),
        "from_attributes": True,
    }

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))
