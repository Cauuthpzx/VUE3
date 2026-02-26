from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any

import bcrypt
import jwt
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.repositories.token_repository import TokenRepository

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


async def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC).replace(tzinfo=None) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "token_type": TokenType.ACCESS})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def create_refresh_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC).replace(tzinfo=None) + (
        expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    to_encode.update({"exp": expire, "token_type": TokenType.REFRESH})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def verify_token(
    token: str, expected_token_type: TokenType, db: AsyncSession
) -> dict[str, Any] | None:
    token_repo = TokenRepository(db)
    if await token_repo.is_blacklisted(token):
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub: str | None = payload.get("sub")
        token_type: str | None = payload.get("token_type")

        if sub is None or token_type != expected_token_type:
            return None

        return {"sub": sub}
    except jwt.PyJWTError:
        return None
