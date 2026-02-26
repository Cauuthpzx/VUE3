from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Cấu hình ứng dụng, đọc từ biến môi trường hoặc file .env."""

    APP_NAME: str = "Backend API"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # PostgreSQL
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/app_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
