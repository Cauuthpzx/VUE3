"""Pydantic schemas cho Agent CRUD."""

from pydantic import BaseModel, Field


class AgentCreate(BaseModel):
    owner: str = Field(description="Tên chủ sở hữu / đại lý")
    username: str = Field(description="Tên tài khoản upstream")
    base_url: str = Field(description="URL nền tảng upstream (e.g. https://xxx.ee88dly.com)")
    cookie: str | None = Field(default=None, description="Cookie string (nếu có sẵn)")
    password: str | None = Field(default=None, description="Mật khẩu upstream (sẽ được mã hóa)")


class AgentRead(BaseModel):
    id: int
    owner: str
    username: str
    base_url: str
    cookie_set: bool = Field(description="Có cookie hay chưa")
    password_set: bool = Field(description="Có mật khẩu hay chưa")
    is_active: bool
    last_login_at: str | None = None
    created_at: str | None = None


class AgentUpdate(BaseModel):
    owner: str | None = None
    base_url: str | None = None
    cookie: str | None = None
    password: str | None = None
    is_active: bool | None = None
