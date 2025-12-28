from pydantic import BaseModel, EmailStr, validator, Field
from uuid import UUID

class Usercreate(BaseModel):
    username: str
    email: EmailStr
    password: str 
    role: str = Field(default="user")

class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    is_active: bool

    class Config:
        from_attributes = True