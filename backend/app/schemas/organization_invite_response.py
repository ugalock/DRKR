# coding: utf-8

from __future__ import annotations
from datetime import datetime
import pprint

from pydantic import StrictInt, StrictStr, Field

from app.schemas._base_model import CustomBaseModel

class OrganizationInviteResponse(CustomBaseModel):
    id: StrictInt = Field(..., description="Invite ID")
    organization_id: StrictInt = Field(..., description="Organization ID")
    invited_user_id: StrictInt = Field(..., description="ID of the invited user")
    invited_user_name: StrictStr = Field(..., description="Name of the invited user")
    role: StrictStr = Field(..., description="Role assigned to the invited user")
    is_used: bool = Field(..., description="Whether the invite has been used")
    expires_at: str = Field(..., description="When the invite expires")
    created_at: str = Field(..., description="When the invite was created")
    
    model_config = {
        "populate_by_name": True,
        "validate_assignment": False,
        "protected_namespaces": (),
        "from_attributes": True,
    }
    
    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))
