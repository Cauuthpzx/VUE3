from fastapi import APIRouter

from app.api.v1.endpoints import agents, auth, data, health, proxy, sync, users

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(sync.router, prefix="/sync", tags=["sync"])
api_router.include_router(data.router, prefix="/data", tags=["data"])
api_router.include_router(proxy.router, prefix="/proxy", tags=["proxy"])
api_router.include_router(agents.router)
