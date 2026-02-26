from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    name: str = Field(
        min_length=2, max_length=50, description="Họ tên người dùng", examples=["Nguyen Van A"]
    )
    username: str = Field(
        min_length=2,
        max_length=30,
        pattern=r"^[a-z0-9_]+$",
        description="Tên đăng nhập (chỉ chữ thường, số, gạch dưới)",
        examples=["nguyenvana"],
    )
    email: EmailStr = Field(description="Địa chỉ email", examples=["user@example.com"])


class UserCreate(UserBase):
    model_config = ConfigDict(extra="forbid")
    password: str = Field(
        min_length=8, description="Mật khẩu (tối thiểu 8 ký tự)", examples=["Str0ngP@ss!"]
    )


class UserCreateInternal(UserBase):
    hashed_password: str = Field(description="Mật khẩu đã được hash")


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="ID người dùng")
    name: str = Field(description="Họ tên người dùng")
    username: str = Field(description="Tên đăng nhập")
    email: EmailStr = Field(description="Địa chỉ email")
    is_active: bool = Field(description="Trạng thái hoạt động")
    is_superuser: bool = Field(description="Quyền quản trị viên")
    created_at: datetime = Field(description="Thời gian tạo tài khoản")


class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(
        None, min_length=2, max_length=50, description="Họ tên mới"
    )
    username: str | None = Field(
        None,
        min_length=2,
        max_length=30,
        pattern=r"^[a-z0-9_]+$",
        description="Tên đăng nhập mới",
    )
    email: EmailStr | None = Field(None, description="Email mới")
