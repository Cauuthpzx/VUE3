"""Agent CRUD router — quản lý tài khoản upstream agent."""

import asyncio
import logging
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import async_get_db
from app.models.agent import Agent
from app.repositories.agent_repository import AgentRepository
from app.repositories.sync_repository import SyncRepository
from app.schemas.agent import AgentCreate, AgentUpdate
from app.services.agent_login_service import (
    AgentLoginService,
    cookie_dict_to_str,
    cookie_str_to_dict,
    decrypt_password,
    encrypt_password,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/agents",
    tags=["agents"],
)

# Per-agent locks to prevent concurrent login/check operations on same agent.
# Bounded: evicts oldest unlocked entries when exceeding MAX_LOCKS to prevent
# unbounded memory growth over the lifetime of the process.
_agent_locks: dict[str, asyncio.Lock] = {}
_MAX_LOCKS = 200


def _get_agent_lock(agent_id: int, operation: str) -> asyncio.Lock:
    """Get or create a lock for a specific agent+operation combo."""
    key = f"{agent_id}:{operation}"
    if key not in _agent_locks:
        # Evict unlocked entries when cache is full
        if len(_agent_locks) >= _MAX_LOCKS:
            to_delete = [k for k, v in _agent_locks.items() if not v.locked()]
            for k in to_delete[:len(to_delete) // 2]:  # evict half of unlocked
                del _agent_locks[k]
        _agent_locks[key] = asyncio.Lock()
    return _agent_locks[key]


def _serialize(agent: Agent) -> dict[str, Any]:
    """Serialize agent — cookie và password_enc KHÔNG bao giờ lộ ra ngoài."""
    return {
        "id": agent.id,
        "owner": agent.owner,
        "username": agent.username,
        "base_url": agent.base_url,
        "cookie_set": bool(agent.cookie),
        "cookie_status": agent.cookie_status or ("none" if not agent.cookie else "unknown"),
        "password_set": bool(agent.password_enc),
        "is_active": agent.is_active,
        "last_login_at": (
            agent.last_login_at.isoformat() if agent.last_login_at else None
        ),
        "created_at": (
            agent.created_at.isoformat() if agent.created_at else None
        ),
    }


@router.get(
    "",
    summary="Danh sách agents",
    description="Lấy danh sách tất cả agents đang hoạt động.",
)
async def list_agents(
    db: AsyncSession = Depends(async_get_db),
    _: dict = Depends(get_current_user),
) -> dict:
    repo = AgentRepository(db)
    agents = await repo.list_active()
    return {
        "code": 0,
        "message": "success",
        "data": {"agents": [_serialize(a) for a in agents]},
        "errors": [],
    }


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Tạo agent mới",
    description="Thêm tài khoản upstream agent. Nếu trùng username đã bị xóa mềm thì khôi phục — dữ liệu cũ được giữ nguyên.",
)
async def create_agent(
    body: AgentCreate,
    db: AsyncSession = Depends(async_get_db),
    _: dict = Depends(get_current_user),
) -> dict:
    repo = AgentRepository(db)
    base_url = body.base_url.rstrip("/")

    # Match by username only — cùng đại lý dù đổi URL vẫn giữ dữ liệu
    existing = await repo.find_by_username(body.username)

    if existing:
        if existing.is_active:
            return {
                "code": 1,
                "message": f"Account '{body.username}' already exists.",
                "data": None,
                "errors": [],
            }
        # Tài khoản đã bị xóa mềm → khôi phục, giữ nguyên dữ liệu + cookie + password cũ
        values: dict[str, Any] = {
            "is_active": True,
            "owner": body.owner,
            "base_url": base_url,
        }
        if body.password:
            values["password_enc"] = encrypt_password(body.password)
        await repo.update_fields(existing.id, values)
        existing = await repo.refresh(existing)
        return {
            "code": 0,
            "message": "Agent restored",
            "data": {"agent": _serialize(existing)},
            "errors": [],
        }

    agent = Agent(
        owner=body.owner,
        username=body.username,
        base_url=base_url,
        cookie=body.cookie,
        password_enc=encrypt_password(body.password) if body.password else None,
    )
    agent = await repo.create(agent)
    return {
        "code": 0,
        "message": "Agent created",
        "data": {"agent": _serialize(agent)},
        "errors": [],
    }


@router.patch(
    "/{agent_id}",
    summary="Cập nhật agent",
    description="Cập nhật thông tin agent (owner, base_url, cookie, password, is_active).",
)
async def update_agent(
    agent_id: int,
    body: AgentUpdate,
    db: AsyncSession = Depends(async_get_db),
    _: dict = Depends(get_current_user),
) -> dict:
    repo = AgentRepository(db)
    agent = await repo.get_by_id(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found",
        )

    values: dict[str, Any] = {
        k: v
        for k, v in body.model_dump().items()
        if v is not None and k != "password"
    }
    if "base_url" in values:
        values["base_url"] = values["base_url"].rstrip("/")
    if body.password:
        values["password_enc"] = encrypt_password(body.password)

    await repo.update_fields(agent_id, values)
    agent = await repo.refresh(agent)
    return {
        "code": 0,
        "message": "Agent updated",
        "data": {"agent": _serialize(agent)},
        "errors": [],
    }


@router.delete(
    "/{agent_id}",
    summary="Xóa agent (soft delete)",
    description="Vô hiệu hóa agent (is_active = False).",
)
async def delete_agent(
    agent_id: int,
    db: AsyncSession = Depends(async_get_db),
    _: dict = Depends(get_current_user),
) -> dict:
    repo = AgentRepository(db)
    agent = await repo.get_by_id(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found",
        )
    await repo.soft_delete(agent_id)
    return {"code": 0, "message": "Agent deactivated", "data": None, "errors": []}


@router.delete(
    "/{agent_id}/data",
    summary="Xóa dữ liệu agent",
    description="Xóa toàn bộ dữ liệu đồng bộ của agent (bets, members, deposits, withdrawals, reports, sync logs, sync locks). "
                "KHÔNG xóa tài khoản agent — chỉ xóa data.",
)
async def clear_agent_data(
    agent_id: int,
    db: AsyncSession = Depends(async_get_db),
    _: dict = Depends(get_current_user),
) -> dict:
    repo = AgentRepository(db)
    agent = await repo.get_by_id(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found",
        )
    sync_repo = SyncRepository(db)
    await sync_repo.clear_all(agent_id)
    return {
        "code": 0,
        "message": "Agent data cleared",
        "data": {"agent_id": agent_id, "username": agent.username},
        "errors": [],
    }


@router.post(
    "/{agent_id}/login",
    summary="Đăng nhập agent",
    description="Trigger đăng nhập thủ công cho agent — lấy cookie mới từ upstream (auto captcha OCR). "
                "Per-agent lock ngăn chặn login trùng lặp đồng thời.",
)
async def login_agent(
    agent_id: int,
    db: AsyncSession = Depends(async_get_db),
    _: dict = Depends(get_current_user),
) -> dict:
    lock = _get_agent_lock(agent_id, "login")
    if lock.locked():
        return {
            "code": 1,
            "message": "Agent is being logged in, please wait.",
            "data": None,
            "errors": [],
        }

    async with lock:
        repo = AgentRepository(db)
        agent = await repo.get_by_id(agent_id)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found",
            )

        if not agent.password_enc:
            return {
                "code": 1,
                "message": "Agent has no password. Please update password first.",
                "data": None,
                "errors": [],
            }

        plain_pw = decrypt_password(agent.password_enc)
        svc = AgentLoginService(agent.base_url)

        try:
            ok, msg, cookies_dict = await asyncio.to_thread(
                svc.login, agent.username, plain_pw
            )
        finally:
            svc.close()

        if not ok:
            return {"code": 1, "message": msg, "data": None, "errors": []}

        new_cookie = cookie_dict_to_str(cookies_dict)
        logger.info(
            "Lưu cookie cho agent %d (%s): %d ký tự, keys=%s",
            agent_id, agent.owner, len(new_cookie), list(cookies_dict.keys()),
        )
        now = datetime.now(UTC)
        await repo.update_fields(agent_id, {
            "cookie": new_cookie,
            "cookie_status": "valid",
            "last_login_at": now,
        })

        return {
            "code": 0,
            "message": "Login successful",
            "data": {"cookie_set": True, "last_login_at": now.isoformat()},
            "errors": [],
        }


@router.post(
    "/{agent_id}/check-cookie",
    summary="Kiểm tra cookie",
    description="Kiểm tra cookie của agent còn hiệu lực không. "
                "Per-agent lock ngăn chặn check trùng lặp đồng thời.",
)
async def check_agent_cookie(
    agent_id: int,
    db: AsyncSession = Depends(async_get_db),
    _: dict = Depends(get_current_user),
) -> dict:
    lock = _get_agent_lock(agent_id, "check")
    if lock.locked():
        return {
            "code": 0,
            "message": "success",
            "data": {"is_valid": None, "message": "Checking in progress, please wait."},
            "errors": [],
        }

    async with lock:
        repo = AgentRepository(db)
        agent = await repo.get_by_id(agent_id)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found",
            )

        if not agent.cookie:
            return {
                "code": 0,
                "message": "success",
                "data": {"is_valid": False, "message": "No cookie available"},
                "errors": [],
            }

        cookies_dict = cookie_str_to_dict(agent.cookie)
        svc = AgentLoginService(agent.base_url)

        try:
            is_valid, msg = await asyncio.to_thread(svc.check_cookies_live, cookies_dict)
        finally:
            svc.close()

        # Cập nhật cookie_status trong DB
        new_status = "valid" if is_valid else "expired"
        await repo.update_fields(agent_id, {"cookie_status": new_status})

        return {
            "code": 0,
            "message": "success",
            "data": {"is_valid": is_valid, "message": msg, "cookie_status": new_status},
            "errors": [],
        }
