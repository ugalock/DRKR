# coding: utf-8

"""
    DRKR API

    A sample OpenAPI specification for the DRKR project, covering all endpoint stubs across authentication, users, organizations, deep research items, tags, comments, ratings, research jobs, and search. 

    The version of the OpenAPI document: 1.0.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501

from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from pydantic import BaseModel, ConfigDict, StrictBool, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

from app.schemas._base_model import CustomBaseModel

class TagUpdateRequest(CustomBaseModel):
    """
    TagUpdateRequest
    """ # noqa: E501
    name: Optional[StrictStr] = None
    is_global: Optional[StrictBool] = None
    __properties: ClassVar[List[str]] = ["name", "is_global"]

    model_config = {
        "populate_by_name": True,
        "validate_assignment": False,
        "protected_namespaces": (),
    }


    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))



