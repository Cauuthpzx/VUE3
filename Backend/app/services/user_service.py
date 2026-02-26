from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = UserRepository(db)

    async def register(self, user_in: UserCreate) -> User:
        if await self.repo.get_by_email(user_in.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email đã được đăng ký.",
            )
        if await self.repo.get_by_username(user_in.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username đã tồn tại.",
            )

        user = User(
            name=user_in.name,
            username=user_in.username,
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
        )
        return await self.repo.create(user)

    async def get_user(self, user_id: int) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy người dùng.",
            )
        return user

    async def get_user_including_deleted(self, user_id: int) -> User:
        user = await self.repo.get_by_id(user_id, include_deleted=True)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy người dùng.",
            )
        return user

    async def list_users(self, skip: int = 0, limit: int = 20) -> list[User]:
        return await self.repo.list_active(skip=skip, limit=limit)

    async def update_user(
        self, user_id: int, values: UserUpdate, current_user: dict[str, Any]
    ) -> User:
        if current_user["id"] != user_id and not current_user["is_superuser"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không đủ quyền cập nhật.",
            )

        user = await self.get_user(user_id)
        update_data = values.model_dump(exclude_unset=True)

        if "email" in update_data and update_data["email"] != user.email:
            if await self.repo.email_exists(update_data["email"]):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email đã được đăng ký.",
                )

        if "username" in update_data and update_data["username"] != user.username:
            if await self.repo.username_exists(update_data["username"]):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Username đã tồn tại.",
                )

        return await self.repo.update(user, update_data)

    async def delete_user(
        self, user_id: int, current_user: dict[str, Any]
    ) -> None:
        if current_user["id"] != user_id and not current_user["is_superuser"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không đủ quyền xóa.",
            )
        user = await self.get_user(user_id)
        await self.repo.soft_delete(user)

    async def hard_delete_user(self, user_id: int) -> None:
        user = await self.get_user_including_deleted(user_id)
        await self.repo.hard_delete(user)
