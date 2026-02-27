import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.core.middleware import RequestIDMiddleware
from app.db.session import close_db, init_db
from app.services.upstream_proxy import close_httpx_client

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Khởi động ứng dụng")
    await init_db()
    yield
    await close_httpx_client()
    await close_db()
    logger.info("Tắt ứng dụng")


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(RequestIDMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=500)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(
        "Lỗi không xử lý: %s",
        str(exc),
        exc_info=True,
        extra={"request_id": request_id},
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Lỗi hệ thống. Vui lòng thử lại sau."},
        headers={"X-Request-ID": request_id},
    )


app.include_router(api_router, prefix=settings.API_V1_PREFIX)
