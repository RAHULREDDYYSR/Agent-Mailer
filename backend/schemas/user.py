from pydantic import BaseModel, EmailStr, validator, Field
from uuid import UUID

class Usercreate(BaseModel):
    username: str
    email: EmailStr
    password: str 
    role: str = Field(default="user")
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    linkedin: str | None = None
    github: str | None = None
    portfolio: str | None = None

class UserRead(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    is_active: bool
    role: str
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    linkedin: str | None = None
    github: str | None = None
    portfolio: str | None = None
    user_context: str | None = None

    class Config:
        from_attributes = True