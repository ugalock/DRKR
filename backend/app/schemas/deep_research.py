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
from datetime import datetime

from pydantic import BaseModel, ConfigDict, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

class DeepResearch(BaseModel):
    """
    DeepResearch
    """ # noqa: E501
    id: StrictInt
    user_id: StrictInt
    owner_user_id: Optional[StrictInt] = None
    owner_org_id: Optional[StrictInt] = None
    visibility: StrictStr
    title: StrictStr
    prompt_text: StrictStr
    final_report: StrictStr
    model_name: Optional[StrictStr] = None
    model_params: Optional[StrictStr] = None
    source_count: Optional[StrictInt] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    __properties: ClassVar[List[str]] = ["id", "user_id", "owner_user_id", "owner_org_id", "visibility", "title", "prompt_text", "final_report", "model_name", "model_params", "source_count", "created_at", "updated_at"]

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
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of DeepResearch from a JSON string"""
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
        """Create an instance of DeepResearch from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "user_id": obj.get("user_id"),
            "owner_user_id": obj.get("owner_user_id"),
            "owner_org_id": obj.get("owner_org_id"),
            "visibility": obj.get("visibility"),
            "title": obj.get("title"),
            "prompt_text": obj.get("prompt_text"),
            "final_report": obj.get("final_report"),
            "model_name": obj.get("model_name"),
            "model_params": obj.get("model_params"),
            "source_count": obj.get("source_count"),
        })
        return _


