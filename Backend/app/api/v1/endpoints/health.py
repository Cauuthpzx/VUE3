from fastapi import APIRouter

from app.schemas.common import HealthResponse

router = APIRouter()


@router.get(
    "/",
    response_model=HealthResponse,
    summary="Kiểm tra sức khoẻ hệ thống",
    description="Trả về trạng thái hoạt động của API server.",
)
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}
