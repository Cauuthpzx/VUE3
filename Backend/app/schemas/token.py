from datetime import datetime

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    sub: str


class TokenBlacklistCreate(BaseModel):
    token: str
    expires_at: datetime
