from datetime import datetime, timedelta
from typing import Any

import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    ALGORITHM,
    SECRET_KEY,
    TokenType,
    create_access_token,
    create_refresh_token,
    verify_password,
)
from app.repositories.token_repository import TokenRepository
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.user_repo = UserRepository(db)
        self.token_repo = TokenRepository(db)

    async def authenticate(
        self, username_or_email: str, password: str
    ) -> dict[str, Any] | None:
        user = await self.user_repo.get_by_username_or_email(username_or_email)
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

    async def create_tokens(
        self, username: str
    ) -> tuple[str, str]:
        access_token = await create_access_token(data={"sub": username})
        refresh_token = await create_refresh_token(data={"sub": username})
        return access_token, refresh_token

    async def verify_refresh_token(self, token: str) -> dict[str, Any] | None:
        if await self.token_repo.is_blacklisted(token):
            return None

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            sub: str | None = payload.get("sub")
            token_type: str | None = payload.get("token_type")

            if sub is None or token_type != TokenType.REFRESH:
                return None

            return {"sub": sub}
        except jwt.PyJWTError:
            return None

    async def blacklist_token(self, token: str) -> None:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            exp_timestamp = payload.get("exp")
            if exp_timestamp is not None:
                expires_at = datetime.fromtimestamp(exp_timestamp)
                await self.token_repo.blacklist(token, expires_at)
        except jwt.PyJWTError:
            pass

    async def blacklist_tokens(
        self, access_token: str, refresh_token: str
    ) -> None:
        for token in [access_token, refresh_token]:
            await self.blacklist_token(token)
