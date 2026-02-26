from typing import Annotated, Any

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import TokenType, oauth2_scheme, verify_token
from app.db.session import async_get_db
from app.models.user import User


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, Any]:
    token_data = await verify_token(token, TokenType.ACCESS, db)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Không thể xác thực người dùng.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    sub = token_data["sub"]
    if "@" in sub:
        stmt = select(User).where(User.email == sub, User.is_deleted == False)  # noqa: E712
    else:
        stmt = select(User).where(User.username == sub, User.is_deleted == False)  # noqa: E712

    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Không thể xác thực người dùng.",
        )

    return {
        "id": user.id,
        "name": user.name,
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
    }


async def get_optional_user(
    request: Request,
    db: AsyncSession = Depends(async_get_db),
) -> dict[str, Any] | None:
    token = request.headers.get("Authorization")
    if not token:
        return None

    try:
        token_type, _, token_value = token.partition(" ")
        if token_type.lower() != "bearer" or not token_value:
            return None

        token_data = await verify_token(token_value, TokenType.ACCESS, db)
        if token_data is None:
            return None

        return await get_current_user(token_value, db=db)
    except HTTPException:
        return None


async def get_current_superuser(
    current_user: Annotated[dict, Depends(get_current_user)],
) -> dict:
    if not current_user["is_superuser"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không đủ quyền truy cập.",
        )
    return current_user
