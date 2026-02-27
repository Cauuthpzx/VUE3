import json
import logging

from fastapi import APIRouter, BackgroundTasks, Depends, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.security import TokenType, verify_token
from app.db.session import async_get_db, async_session
from app.repositories.agent_repository import AgentRepository
from app.schemas.sync import SyncRequest
from app.services.sync_service import SyncService

logger = logging.getLogger(__name__)
router = APIRouter()


async def _mark_cookie_expired(agent_id: int, db: AsyncSession | None = None) -> None:
    """Đánh dấu cookie_status = expired khi sync phát hiện cookie hết hạn."""
    try:
        if db:
            repo = AgentRepository(db)
            await repo.update_fields(agent_id, {"cookie_status": "expired"})
        else:
            async with async_session() as new_db:
                repo = AgentRepository(new_db)
                await repo.update_fields(agent_id, {"cookie_status": "expired"})
    except Exception:
        logger.exception("Không thể đánh dấu cookie hết hạn cho agent %d", agent_id)


def _has_cookie_error(result: dict) -> bool:
    """Kiểm tra kết quả sync có lỗi cookie expired không."""
    results = result.get("results", {})
    for r in results.values():
        err = str(r.get("error", "")).lower() if isinstance(r, dict) else ""
        if "cookie" in err:
            return True
    return False


@router.post(
    "/trigger",
    status_code=status.HTTP_200_OK,
    summary="Trigger data sync",
    description="Fetch data from the source site and save to local database.",
)
async def trigger_sync(
    req: SyncRequest,
    db: AsyncSession = Depends(async_get_db),
    _: dict = Depends(get_current_user),
) -> dict:
    cookies = req.cookies
    logger.info("Kích hoạt đồng bộ: agent_id=%s", req.agent_id)
    if cookies == "__from_agent__" and req.agent_id:
        agent_repo = AgentRepository(db)
        agent = await agent_repo.get_active_by_id(req.agent_id)
        if agent and agent.cookie:
            cookies = agent.cookie
            logger.info("Đã lấy cookie từ DB cho agent %s: %d ký tự", req.agent_id, len(cookies))
        else:
            logger.warning("Agent %s không có cookie", req.agent_id)
            return {"error": "Agent không có cookie. Vui lòng Login agent trước."}

    service = SyncService(db)
    result = await service.sync_all(
        base_url=req.base_url,
        cookies=cookies,
        agent_id=req.agent_id,
        data_date=req.data_date,
        max_pages=req.max_pages,
        endpoints=req.endpoints,
    )

    # Cập nhật cookie_status nếu phát hiện expired
    if _has_cookie_error(result):
        await _mark_cookie_expired(req.agent_id, db)

    return result


@router.post(
    "/trigger-background",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger data sync in background",
    description="Start sync as a background task. Returns immediately.",
)
async def trigger_sync_background(
    req: SyncRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(async_get_db),
    _: dict = Depends(get_current_user),
) -> dict:
    # Pre-resolve cookie
    cookies = req.cookies
    if cookies == "__from_agent__" and req.agent_id:
        agent_repo = AgentRepository(db)
        agent = await agent_repo.get_active_by_id(req.agent_id)
        if agent and agent.cookie:
            cookies = agent.cookie
        else:
            return {"error": "Agent không có cookie. Vui lòng Login agent trước."}

    async def run_sync():
        async with async_session() as bg_db:
            service = SyncService(bg_db)
            try:
                result = await service.sync_all(
                    base_url=req.base_url,
                    cookies=cookies,
                    agent_id=req.agent_id,
                    data_date=req.data_date,
                    max_pages=req.max_pages,
                    endpoints=req.endpoints,
                )
                logger.info("Đồng bộ nền hoàn tất cho agent %s", req.agent_id)
                if _has_cookie_error(result):
                    await _mark_cookie_expired(req.agent_id, bg_db)
            except Exception:
                logger.exception("Đồng bộ nền thất bại cho agent %s", req.agent_id)

    background_tasks.add_task(run_sync)
    return {"message": "Đã bắt đầu đồng bộ nền", "agent_id": req.agent_id}


@router.websocket("/ws")
async def sync_websocket(
    ws: WebSocket,
    token: str = Query(...),
):
    """WebSocket endpoint cho realtime sync progress.

    Client kết nối ws://host/api/v1/sync/ws?token=JWT_TOKEN
    → Gửi JSON config (SyncRequest fields) → Nhận từng kết quả endpoint realtime.
    """
    # ── Auth qua query param ──
    async with async_session() as db:
        payload = await verify_token(token, TokenType.ACCESS, db)
        if payload is None:
            await ws.close(code=4001, reason="Invalid token")
            return

    await ws.accept()

    try:
        # ── Nhận config từ client (message đầu tiên) ──
        raw = await ws.receive_text()
        try:
            config = json.loads(raw)
        except json.JSONDecodeError:
            await ws.send_json({"type": "error", "message": "Invalid JSON"})
            await ws.close()
            return

        req = SyncRequest(**config)

        # ── Resolve cookie từ agent DB nếu cần ──
        cookies = req.cookies
        logger.info("WS đồng bộ: agent_id=%s", req.agent_id)
        if cookies == "__from_agent__" and req.agent_id:
            async with async_session() as db:
                agent_repo = AgentRepository(db)
                agent = await agent_repo.get_active_by_id(req.agent_id)
                if agent and agent.cookie:
                    cookies = agent.cookie
                    logger.info(
                        "WS đồng bộ: lấy cookie từ DB cho agent %d, %d ký tự",
                        req.agent_id, len(cookies),
                    )
                else:
                    logger.warning(
                        "WS đồng bộ: agent %d không có cookie",
                        req.agent_id,
                    )
                    await ws.send_json({
                        "type": "error",
                        "message": "Agent không có cookie. Vui lòng Login agent trước.",
                    })
                    await ws.close()
                    return

        # ── Track cookie expired for status update ──
        cookie_expired_detected = False

        # ── Callback gửi progress qua WS ──
        async def on_progress(msg: dict) -> None:
            nonlocal cookie_expired_detected
            try:
                await ws.send_json(msg)
            except Exception:
                pass  # client đã ngắt kết nối

            # Detect cookie expired from progress messages
            if msg.get("type") == "progress":
                result = msg.get("result", {})
                if isinstance(result, dict):
                    err = str(result.get("error", "")).lower()
                    if "cookie" in err:
                        cookie_expired_detected = True

        # ── Chạy sync với session mới (vì WS sống lâu) ──
        async with async_session() as db:
            service = SyncService(db)
            await service.sync_all(
                base_url=req.base_url,
                cookies=cookies,
                agent_id=req.agent_id,
                data_date=req.data_date,
                max_pages=req.max_pages,
                endpoints=req.endpoints,
                on_progress=on_progress,
            )

        # Cập nhật cookie_status nếu phát hiện expired
        if cookie_expired_detected:
            await _mark_cookie_expired(req.agent_id)

    except WebSocketDisconnect:
        logger.info("WS đồng bộ: client ngắt kết nối")
    except Exception as e:
        logger.exception("WS đồng bộ: lỗi không xác định")
        try:
            await ws.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
    finally:
        try:
            await ws.close()
        except Exception:
            pass
