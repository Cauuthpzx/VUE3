from typing import Annotated, Any

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.rate_limit import check_auth_rate_limit
from app.core.security import oauth2_scheme
from app.db.session import async_get_db
from app.schemas.common import MessageResponse
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserRead
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter()


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký tài khoản",
    description="Tạo tài khoản mới với email, username và mật khẩu. Trả về 409 nếu email hoặc username đã tồn tại.",
)
async def register(
    user_in: UserCreate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    _rate_limit: None = Depends(check_auth_rate_limit),
) -> Any:
    service = UserService(db)
    return await service.register(user_in)


@router.post(
    "/login",
    response_model=Token,
    summary="Đăng nhập",
    description="Xác thực bằng username/email + mật khẩu. Trả về access token và set refresh token vào httpOnly cookie.",
)
async def login(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(async_get_db)],
    _rate_limit: None = Depends(check_auth_rate_limit),
) -> dict[str, str]:
    auth_service = AuthService(db)
    user = await auth_service.authenticate(
        username_or_email=form_data.username,
        password=form_data.password,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sai tên đăng nhập, email hoặc mật khẩu.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token, refresh_token = await auth_service.create_tokens(user["username"])

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


@router.post(
    "/refresh",
    response_model=Token,
    summary="Làm mới access token",
    description="Dùng refresh token từ cookie để lấy access token mới.",
)
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

    auth_service = AuthService(db)
    user_data = await auth_service.verify_refresh_token(refresh_token)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token không hợp lệ.",
        )

    access_token, _ = await auth_service.create_tokens(user_data["sub"])
    return {"access_token": access_token, "token_type": "bearer"}


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Đăng xuất",
    description="Blacklist access token và refresh token, xoá cookie.",
)
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

    auth_service = AuthService(db)
    await auth_service.blacklist_tokens(
        access_token=access_token,
        refresh_token=refresh_token,
    )
    response.delete_cookie(key="refresh_token")

    return {"message": "Đăng xuất thành công."}
