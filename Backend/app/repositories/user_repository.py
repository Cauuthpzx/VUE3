from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, user_id: int, include_deleted: bool = False) -> User | None:
        stmt = select(User).where(User.id == user_id)
        if not include_deleted:
            stmt = stmt.where(User.is_deleted == False)  # noqa: E712
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str, include_deleted: bool = False) -> User | None:
        stmt = select(User).where(User.email == email)
        if not include_deleted:
            stmt = stmt.where(User.is_deleted == False)  # noqa: E712
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str, include_deleted: bool = False) -> User | None:
        stmt = select(User).where(User.username == username)
        if not include_deleted:
            stmt = stmt.where(User.is_deleted == False)  # noqa: E712
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username_or_email(self, identifier: str) -> User | None:
        if "@" in identifier:
            return await self.get_by_email(identifier)
        return await self.get_by_username(identifier)

    async def email_exists(self, email: str) -> bool:
        result = await self.db.execute(
            select(func.count()).select_from(User).where(User.email == email)
        )
        return bool(result.scalar())

    async def username_exists(self, username: str) -> bool:
        result = await self.db.execute(
            select(func.count()).select_from(User).where(User.username == username)
        )
        return bool(result.scalar())

    async def list_active(self, skip: int = 0, limit: int = 20) -> list[User]:
        stmt = (
            select(User)
            .where(User.is_deleted == False)  # noqa: E712
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update(self, user: User, update_data: dict) -> User:
        for field, value in update_data.items():
            setattr(user, field, value)
        user.updated_at = datetime.now(UTC)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def soft_delete(self, user: User) -> None:
        user.is_deleted = True
        user.deleted_at = datetime.now(UTC)
        await self.db.commit()

    async def hard_delete(self, user: User) -> None:
        await self.db.delete(user)
        await self.db.commit()
