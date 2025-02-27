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

from pydantic import BaseModel, ConfigDict, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

class ResearchJobAnswerRequest(BaseModel):
    """
    ResearchJobAnswerRequest
    """ # noqa: E501
    service: StrictStr
    job_id: StrictStr
    answers: List[StrictStr]
    __properties: ClassVar[List[str]] = ["service", "job_id", "answers"]

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "protected_namespaces": (),
        "json_schema_extra": {
            "example": {
                "service": "open-dr",
                "job_id": "123e4567-e89b-12d3-a456-426614174000",
                "answers": [
                    "Answer to first follow-up question",
                    "Answer to second follow-up question"
                ]
            }
        }
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
        """Create an instance of ResearchJobAnswerRequest from a JSON string"""
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
        """Create an instance of ResearchJobAnswerRequest from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "service": obj.get("service"),
            "job_id": obj.get("job_id"),
            "answers": obj.get("answers")
        })
        return _obj 