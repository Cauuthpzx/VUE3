import logging
from collections.abc import AsyncGenerator

import redis.asyncio as aioredis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

logger = logging.getLogger(__name__)

async_engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)

async_session = async_sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)

redis_client: aioredis.Redis | None = None


async def async_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def get_redis() -> aioredis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return redis_client


async def seed_admin() -> None:
    from app.core.security import get_password_hash
    from app.models.user import User

    async with async_session() as db:
        result = await db.execute(select(User).where(User.username == "admin"))
        if result.scalar_one_or_none() is not None:
            return

        admin = User(
            name="Admin",
            username="admin",
            email="admin@admin.com",
            hashed_password=get_password_hash("admin"),
            is_active=True,
            is_superuser=True,
        )
        db.add(admin)
        await db.commit()
        logger.info("Default admin account created (admin/admin)")


async def init_db() -> None:
    global redis_client
    redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    await seed_admin()


async def close_db() -> None:
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None
    await async_engine.dispose()
