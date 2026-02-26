from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    TokenType,
    authenticate_user,
    blacklist_tokens,
    create_access_token,
    create_refresh_token,
    get_password_hash,
    oauth2_scheme,
    verify_token,
)
from app.db.session import async_get_db
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserRead

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> Any:
    # Kiểm tra email đã tồn tại
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email đã được đăng ký.",
        )

    # Kiểm tra username đã tồn tại
    result = await db.execute(select(User).where(User.username == user_in.username))
    if result.scalar_one_or_none():
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
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@router.post("/login", response_model=Token)
async def login(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, str]:
    user = await authenticate_user(
        username_or_email=form_data.username,
        password=form_data.password,
        db=db,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sai tên đăng nhập, email hoặc mật khẩu.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = await create_access_token(
        data={"sub": user["username"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = await create_refresh_token(data={"sub": user["username"]})

    max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=max_age,
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, str]:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token không tìm thấy.",
        )

    user_data = await verify_token(refresh_token, TokenType.REFRESH, db)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token không hợp lệ.",
        )

    new_access_token = await create_access_token(data={"sub": user_data["sub"]})
    return {"access_token": new_access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(
    response: Response,
    access_token: str = Depends(oauth2_scheme),
    refresh_token: str | None = Cookie(None, alias="refresh_token"),
    db: AsyncSession = Depends(async_get_db),
) -> dict[str, str]:
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token không tìm thấy.",
        )

    await blacklist_tokens(
        access_token=access_token,
        refresh_token=refresh_token,
        db=db,
    )
    response.delete_cookie(key="refresh_token")

    return {"message": "Đăng xuất thành công."}
