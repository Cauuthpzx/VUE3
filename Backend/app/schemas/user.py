from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    name: str = Field(min_length=2, max_length=50, examples=["Nguyen Van A"])
    username: str = Field(
        min_length=2, max_length=30, pattern=r"^[a-z0-9_]+$", examples=["nguyenvana"]
    )
    email: EmailStr = Field(examples=["user@example.com"])


class UserCreate(UserBase):
    model_config = ConfigDict(extra="forbid")
    password: str = Field(min_length=8, examples=["Str0ngP@ss!"])


class UserCreateInternal(UserBase):
    hashed_password: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    username: str
    email: EmailStr
    is_active: bool
    is_superuser: bool
    created_at: datetime


class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(None, min_length=2, max_length=50)
    username: str | None = Field(
        None, min_length=2, max_length=30, pattern=r"^[a-z0-9_]+$"
    )
    email: EmailStr | None = None
