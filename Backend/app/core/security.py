from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any

import bcrypt
import jwt
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings

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


async def authenticate_user(
    username_or_email: str, password: str, db: AsyncSession
) -> dict[str, Any] | None:
    from app.models.user import User

    if "@" in username_or_email:
        stmt = select(User).where(
            User.email == username_or_email, User.is_deleted == False  # noqa: E712
        )
    else:
        stmt = select(User).where(
            User.username == username_or_email, User.is_deleted == False  # noqa: E712
        )

    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        return None
    if not await verify_password(password, user.hashed_password):
        return None

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "name": user.name,
        "is_superuser": user.is_superuser,
        "is_active": user.is_active,
    }


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
    from app.models.token_blacklist import TokenBlacklist

    stmt = select(TokenBlacklist).where(TokenBlacklist.token == token)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
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


async def blacklist_token(token: str, db: AsyncSession) -> None:
    from app.models.token_blacklist import TokenBlacklist

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp_timestamp = payload.get("exp")
        if exp_timestamp is not None:
            expires_at = datetime.fromtimestamp(exp_timestamp)
            db.add(TokenBlacklist(token=token, expires_at=expires_at))
            await db.commit()
    except jwt.PyJWTError:
        pass


async def blacklist_tokens(
    access_token: str, refresh_token: str, db: AsyncSession
) -> None:
    for token in [access_token, refresh_token]:
        await blacklist_token(token, db)
