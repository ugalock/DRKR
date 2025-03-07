from pydantic import BaseModel, Field
from typing import Optional

class OrganizationInviteRequest(BaseModel):
    invited_user_id: int = Field(..., description="ID of the user to invite")
    role: str = Field(..., description="Role to assign to the user (member, admin, owner)") 
