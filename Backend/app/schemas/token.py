from datetime import datetime

from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str = Field(description="JWT access token")
    token_type: str = Field(default="bearer", description="Loại token (luôn là bearer)")


class TokenData(BaseModel):
    sub: str = Field(description="Subject của token (username hoặc email)")


class TokenBlacklistCreate(BaseModel):
    token: str = Field(description="Token cần blacklist")
    expires_at: datetime = Field(description="Thời gian hết hạn của token")
