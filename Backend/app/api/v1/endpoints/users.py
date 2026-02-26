from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_superuser, get_current_user
from app.core.security import oauth2_scheme
from app.db.session import async_get_db
from app.schemas.common import MessageResponse
from app.schemas.user import UserRead, UserUpdate
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter()


@router.get(
    "/",
    response_model=list[UserRead],
    summary="Danh sách người dùng",
    description="Lấy danh sách người dùng đang hoạt động với phân trang.",
)
async def list_users(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> Any:
    service = UserService(db)
    return await service.list_users(skip=skip, limit=limit)


@router.get(
    "/me",
    response_model=UserRead,
    summary="Thông tin người dùng hiện tại",
    description="Lấy thông tin của người dùng đang đăng nhập.",
)
async def read_current_user(
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> Any:
    service = UserService(db)
    return await service.get_user(current_user["id"])


@router.get(
    "/{user_id}",
    response_model=UserRead,
    summary="Chi tiết người dùng",
    description="Lấy thông tin chi tiết của một người dùng theo ID.",
)
async def read_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> Any:
    service = UserService(db)
    return await service.get_user(user_id)


@router.patch(
    "/{user_id}",
    response_model=UserRead,
    summary="Cập nhật người dùng",
    description="Cập nhật thông tin người dùng. Chỉ chủ tài khoản hoặc superuser mới có quyền.",
)
async def update_user(
    user_id: int,
    values: UserUpdate,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> Any:
    service = UserService(db)
    return await service.update_user(user_id, values, current_user)


@router.delete(
    "/{user_id}",
    response_model=MessageResponse,
    summary="Xoá người dùng (soft)",
    description="Soft delete người dùng. Chỉ chủ tài khoản hoặc superuser mới có quyền.",
)
async def delete_user(
    user_id: int,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
    token: str = Depends(oauth2_scheme),
) -> dict[str, str]:
    service = UserService(db)
    await service.delete_user(user_id, current_user)

    # Blacklist token nếu user tự xóa chính mình
    if current_user["id"] == user_id:
        auth_service = AuthService(db)
        await auth_service.blacklist_token(token)

    return {"message": "Xóa người dùng thành công."}


@router.delete(
    "/hard/{user_id}",
    response_model=MessageResponse,
    dependencies=[Depends(get_current_superuser)],
    summary="Xoá vĩnh viễn người dùng",
    description="Xoá vĩnh viễn người dùng khỏi database. Chỉ superuser mới có quyền.",
)
async def hard_delete_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, str]:
    service = UserService(db)
    await service.hard_delete_user(user_id)
    return {"message": "Xóa vĩnh viễn người dùng thành công."}
