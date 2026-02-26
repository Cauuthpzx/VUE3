from datetime import UTC, datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_superuser, get_current_user
from app.core.security import blacklist_token, oauth2_scheme
from app.db.session import async_get_db
from app.models.user import User
from app.schemas.user import UserRead, UserUpdate

router = APIRouter()


@router.get("/", response_model=list[UserRead])
async def list_users(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> Any:
    stmt = (
        select(User)
        .where(User.is_deleted == False)  # noqa: E712
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/me", response_model=UserRead)
async def read_current_user(
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> Any:
    stmt = select(User).where(User.id == current_user["id"])
    result = await db.execute(stmt)
    return result.scalar_one()


@router.get("/{user_id}", response_model=UserRead)
async def read_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> Any:
    stmt = select(User).where(User.id == user_id, User.is_deleted == False)  # noqa: E712
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng.",
        )
    return user


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    values: UserUpdate,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> Any:
    if current_user["id"] != user_id and not current_user["is_superuser"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không đủ quyền cập nhật.",
        )

    stmt = select(User).where(User.id == user_id, User.is_deleted == False)  # noqa: E712
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng.",
        )

    update_data = values.model_dump(exclude_unset=True)

    # Kiểm tra trùng email
    if "email" in update_data and update_data["email"] != user.email:
        exists = await db.execute(
            select(func.count()).where(User.email == update_data["email"])
        )
        if exists.scalar():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email đã được đăng ký.",
            )

    # Kiểm tra trùng username
    if "username" in update_data and update_data["username"] != user.username:
        exists = await db.execute(
            select(func.count()).where(User.username == update_data["username"])
        )
        if exists.scalar():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username đã tồn tại.",
            )

    for field, value in update_data.items():
        setattr(user, field, value)
    user.updated_at = datetime.now(UTC)

    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
    token: str = Depends(oauth2_scheme),
) -> dict[str, str]:
    if current_user["id"] != user_id and not current_user["is_superuser"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không đủ quyền xóa.",
        )

    stmt = select(User).where(User.id == user_id, User.is_deleted == False)  # noqa: E712
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng.",
        )

    # Soft delete
    user.is_deleted = True
    user.deleted_at = datetime.now(UTC)
    await db.commit()

    # Blacklist token nếu user tự xóa chính mình
    if current_user["id"] == user_id:
        await blacklist_token(token, db)

    return {"message": "Xóa người dùng thành công."}


@router.delete("/hard/{user_id}", dependencies=[Depends(get_current_superuser)])
async def hard_delete_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, str]:
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng.",
        )

    await db.delete(user)
    await db.commit()
    return {"message": "Xóa vĩnh viễn người dùng thành công."}
