from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.token_blacklist import TokenBlacklist


class TokenRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def is_blacklisted(self, token: str) -> bool:
        stmt = select(func.count()).select_from(TokenBlacklist).where(
            TokenBlacklist.token == token
        )
        result = await self.db.execute(stmt)
        return (result.scalar() or 0) > 0

    async def blacklist(self, token: str, expires_at: datetime) -> None:
        entry = TokenBlacklist(token=token, expires_at=expires_at)
        self.db.add(entry)
        await self.db.commit()
