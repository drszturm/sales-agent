from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    CASHIER = "cashier"


class User(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    hashed_password: str
    role: UserRole
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True
