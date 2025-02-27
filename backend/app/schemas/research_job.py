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

from pydantic import BaseModel, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional
try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

class ResearchJob(BaseModel):
    """
    ResearchJob
    """ # noqa: E501
    job_id: StrictStr
    user_id: StrictStr
    owner_user_id: Optional[StrictStr] = None
    owner_org_id: Optional[StrictStr] = None
    visibility: StrictStr
    status: StrictStr
    service: StrictStr
    model_name: StrictStr
    model_params: Optional[Dict[str, Any]] = None
    deep_research_id: Optional[StrictStr] = None
    created_at: Optional[StrictStr] = None
    updated_at: Optional[StrictStr] = None
    __properties: ClassVar[List[str]] = ["job_id", "user_id", "owner_user_id", "owner_org_id", "visibility", "status", "service", "model_name", "model_params", "deep_research_id", "created_at", "updated_at"]

    @field_validator('status')
    def status_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('pending_answers', 'running', 'completed', 'failed', 'cancelled'):
            raise ValueError("must be one of enum values ('pending_answers', 'running', 'completed', 'failed', 'cancelled')")
        return value

    @field_validator('visibility')
    def visibility_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('private', 'public', 'org'):
            raise ValueError("must be one of enum values ('private', 'public', 'org')")
        return value

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
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of ResearchJob from a JSON string"""
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
        """Create an instance of ResearchJob from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "job_id": obj.get("job_id"),
            "user_id": obj.get("user_id"),
            "owner_user_id": obj.get("owner_user_id"),
            "owner_org_id": obj.get("owner_org_id"),
            "visibility": obj.get("visibility"),
            "status": obj.get("status"),
            "service": obj.get("service"),
            "model_name": obj.get("model_name"),
            "model_params": obj.get("model_params"),
            "deep_research_id": obj.get("deep_research_id"),
            "created_at": obj.get("created_at"),
            "updated_at": obj.get("updated_at"),
        })
        return _obj


