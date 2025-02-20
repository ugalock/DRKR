# backend/app/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr
    display_name: Optional[str] = None

# For creating a new user
class UserCreate(UserBase):
    password: str  # or handle OAuth differently, as needed

# For reading user data (from DB)
class UserRead(UserBase):
    id: int
    default_role: str

    class Config:
        orm_mode = True

class DeepResearchBase(BaseModel):
    title: str
    prompt_text: str
    final_report: Optional[str] = None
    model_name: Optional[str] = None
    visibility: Optional[str] = "private"

class DeepResearchCreate(DeepResearchBase):
    pass  # Add fields needed for creation

class DeepResearchRead(DeepResearchBase):
    id: int

    class Config:
        orm_mode = True

# Example for API Keys
class ApiKeyBase(BaseModel):
    token: str

class ApiKeyCreate(ApiKeyBase):
    user_id: Optional[int]
    organization_id: Optional[int]

class ApiKeyRead(ApiKeyBase):
    id: int

    class Config:
        orm_mode = True
