"""sync_service.py -- Fetch data from upstream agent site.

Optimized based on reference (server/common.py):
  - limit=5000 (max upstream allows)
  - es=1 always sent
  - Date format: 'YYYY-MM-DD|YYYY-MM-DD' (no space)
  - Retry 3 times + 2s delay between retries
  - Detect expired cookies ('dang nhap' / jump=top)
  - Sequential fetch + 0.3s delay between pages
  - follow_redirects=False
"""

import asyncio
import logging
from collections.abc import Callable
from datetime import UTC, datetime

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.sync_repository import SyncRepository

logger = logging.getLogger(__name__)

# -- Constants (ref: server/common.py) --
LIMIT = 5000
MAX_RETRIES = 3
RETRY_DELAY = 2.0
PAGE_DELAY = 0.3

# Endpoint mapping
ENDPOINTS = {
    "members": "/agent/user.html",
    "invites": "/agent/inviteList.html",
    "bets": "/agent/bet.html",
    "bet_third_party": "/agent/betOrder.html",
    "deposits": "/agent/depositAndWithdrawal.html",
    "withdrawals": "/agent/withdrawalsRecord.html",
    "report_lottery": "/agent/reportLottery.html",
    "report_funds": "/agent/reportFunds.html",
    "report_provider": "/agent/reportThirdGame.html",
}

# Sync rules
NO_DATE_LIMIT = {"members"}
ONCE_PER_DAY_NO_DATE = {"invites"}
REQUIRES_DATE = {
    "bets", "bet_third_party", "deposits", "withdrawals",
    "report_lottery", "report_funds", "report_provider",
}

# Date param name per endpoint
DATE_PARAM_MAP = {
    "bets": "create_time",
    "bet_third_party": "bet_time",
    "deposits": "create_time",
    "withdrawals": "create_time",
    "report_lottery": "hsDateTime",
    "report_funds": "hsDateTime",
    "report_provider": "hsDateTime",
}

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json, text/javascript, */*; q=0.01",
}


def _is_login_required(result: dict) -> bool:
    """Detect upstream login redirect (expired cookie)."""
    msg = str(result.get("msg", "")).lower()
    data = result.get("data")
    return ("dang nhap" in msg
            or "đăng nhập" in msg
            or (isinstance(data, dict) and data.get("jump") == "top"))


class SyncService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = SyncRepository(db)

    async def _fetch_page(
        self,
        client: httpx.AsyncClient,
        path: str,
        *,
        page: int = 1,
        limit: int = LIMIT,
        extra_params: dict | None = None,
    ) -> dict | None:
        """Fetch 1 page with retry logic."""
        data = {"page": str(page), "limit": str(limit), "es": "1"}
        if extra_params:
            data.update(extra_params)

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                resp = await client.post(path, data=data)
                logger.debug(
                    "Tải trang: %s trang %d → HTTP %d, content-type=%s",
                    path, page, resp.status_code,
                    resp.headers.get("content-type", "?")[:50],
                )

                # HTTP 302/301 redirect → cookie expired (follow_redirects=False)
                if resp.status_code in (301, 302):
                    loc = resp.headers.get("Location", "").lower()
                    logger.error(
                        "Chuyển hướng HTTP %d: %s trang %d → %s (cookie hết hạn)",
                        resp.status_code, path, page, loc,
                    )
                    return {"code": -401, "msg": "Cookie hết hạn, vui lòng đăng nhập lại"}

                try:
                    result = resp.json()
                except Exception:
                    logger.error(
                        "Phản hồi không phải JSON: %s trang %d: HTTP %d, body=%s",
                        path, page, resp.status_code, resp.text[:300],
                    )
                    body_lower = resp.text[:500].lower()
                    if "login" in body_lower or "dang nhap" in body_lower:
                        return {"code": -401, "msg": "Cookie hết hạn, vui lòng đăng nhập lại"}
                    return None

                if not isinstance(result, dict):
                    logger.error("Phản hồi không phải dict: %s trang %d", path, page)
                    return None

                if _is_login_required(result):
                    logger.error(
                        "Cookie hết hạn: %s, code=%s, msg=%r",
                        path, result.get("code"), result.get("msg"),
                    )
                    return {"code": -401, "msg": "Cookie hết hạn, vui lòng đăng nhập lại"}

                if result.get("code") == 0:
                    return result

                logger.warning("API lỗi code=%s msg=%s: %s trang %d (lần %d)",
                               result.get("code"), result.get("msg"),
                               path, page, attempt)
                return None

            except httpx.TimeoutException:
                logger.warning("Hết thời gian chờ: %s trang %d (lần %d/%d)",
                               path, page, attempt, MAX_RETRIES)
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(RETRY_DELAY)
            except Exception as e:
                logger.error("Lỗi tải dữ liệu: %s trang %d (lần %d/%d): %s",
                             path, page, attempt, MAX_RETRIES, e)
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(RETRY_DELAY)

        return None

    async def fetch_all_pages(
        self,
        client: httpx.AsyncClient,
        path: str,
        *,
        limit: int = LIMIT,
        max_pages: int = 0,
        extra_params: dict | None = None,
        on_page: Callable[[dict], None] | None = None,
    ) -> tuple[list[dict], int, dict | None]:
        """Fetch all pages sequentially with delay."""
        all_rows: list[dict] = []
        total_data = None

        async def _page_notify(msg: dict) -> None:
            if on_page is None:
                return
            ret = on_page(msg)
            if asyncio.iscoroutine(ret) or asyncio.isfuture(ret):
                await ret

        # Page 1
        first = await self._fetch_page(client, path, page=1, limit=limit,
                                        extra_params=extra_params)
        if not first:
            return [], 0, None

        if first.get("code") == -401:
            return [], 0, {"error": first.get("msg", "Cookie expired")}

        if first.get("code") != 0:
            return [], 0, None

        total_count = first.get("count", 0)
        raw_data = first.get("data", [])
        if isinstance(raw_data, list):
            all_rows.extend(r for r in raw_data if isinstance(r, dict))
        total_data = first.get("total_data")

        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 1
        if max_pages > 0:
            total_pages = min(total_pages, max_pages)

        logger.info("%s: tổng=%d, số trang=%d (trang 1: %d dòng)",
                     path, total_count, total_pages, len(all_rows))

        await _page_notify({
            "phase": "fetching", "page": 1, "total_pages": total_pages,
            "rows_so_far": len(all_rows), "total_count": total_count,
        })

        # Pages 2+ sequential with delay
        for page in range(2, total_pages + 1):
            await asyncio.sleep(PAGE_DELAY)

            result = await self._fetch_page(client, path, page=page, limit=limit,
                                             extra_params=extra_params)
            if not result:
                logger.warning("%s trang %d thất bại, bỏ qua", path, page)
                continue

            if result.get("code") == -401:
                logger.error("%s: cookie hết hạn tại trang %d, dừng lại", path, page)
                break

            if result.get("code") == 0:
                page_data = result.get("data", [])
                if isinstance(page_data, list):
                    all_rows.extend(r for r in page_data if isinstance(r, dict))

            await _page_notify({
                "phase": "fetching", "page": page, "total_pages": total_pages,
                "rows_so_far": len(all_rows), "total_count": total_count,
            })

        return all_rows, total_count, total_data

    async def sync_endpoint(
        self,
        client: httpx.AsyncClient,
        endpoint_key: str,
        agent_id: int,
        *,
        data_date: str | None = None,
        max_pages: int = 0,
        on_detail: Callable[[dict], None] | None = None,
    ) -> dict:
        """Sync 1 endpoint with dedup logic."""
        today = datetime.now(UTC).strftime("%Y-%m-%d")

        async def _detail(msg: dict) -> None:
            if on_detail is None:
                return
            ret = on_detail(msg)
            if asyncio.iscoroutine(ret) or asyncio.isfuture(ret):
                await ret

        # -- Check: invites -> once per day --
        if endpoint_key in ONCE_PER_DAY_NO_DATE:
            if await self.repo.is_synced_today(agent_id, endpoint_key, today):
                return {
                    "endpoint": endpoint_key,
                    "skipped": True,
                    "reason": f"Đã đồng bộ hôm nay ({today})",
                }

        # -- Check: 7 endpoints require date + once per day --
        if endpoint_key in REQUIRES_DATE:
            if not data_date:
                return {
                    "endpoint": endpoint_key,
                    "skipped": True,
                    "reason": "Chưa chọn ngày",
                }
            if await self.repo.is_synced_today(agent_id, endpoint_key, data_date):
                return {
                    "endpoint": endpoint_key,
                    "skipped": True,
                    "reason": f"Đã đồng bộ cho ngày {data_date}",
                }

        # -- Build extra params (date) --
        extra_params: dict | None = None
        if endpoint_key in REQUIRES_DATE and data_date:
            date_field = DATE_PARAM_MAP[endpoint_key]
            # Support range format "start|end" or single date "YYYY-MM-DD"
            if "|" in data_date:
                extra_params = {date_field: data_date}
            else:
                extra_params = {date_field: f"{data_date}|{data_date}"}

        # -- Fetch --
        path = ENDPOINTS[endpoint_key]
        logger.info("Đồng bộ %s từ %s (ngày=%s)", endpoint_key, path, data_date)

        rows, total_count, total_data = await self.fetch_all_pages(
            client, path,
            max_pages=max_pages,
            extra_params=extra_params,
            on_page=on_detail,
        )

        # Check cookie expired
        if isinstance(total_data, dict) and total_data.get("error"):
            return {
                "endpoint": endpoint_key,
                "error": total_data["error"],
                "fetched": 0,
                "total": 0,
                "saved": 0,
            }

        if not rows:
            return {
                "endpoint": endpoint_key,
                "fetched": 0,
                "total": total_count,
                "saved": 0,
            }

        # -- Notify: saving --
        await _detail({
            "phase": "saving", "rows": len(rows), "total_count": total_count,
        })

        # -- Upsert --
        upsert_map = {
            "members": self.repo.upsert_members,
            "invites": self.repo.upsert_invites,
            "bets": self.repo.upsert_bets,
            "bet_third_party": self.repo.upsert_bet_third_party,
            "deposits": self.repo.upsert_deposits,
            "withdrawals": self.repo.upsert_withdrawals,
            "report_lottery": self.repo.upsert_report_lottery,
            "report_funds": self.repo.upsert_report_funds,
            "report_provider": self.repo.upsert_report_provider,
        }

        upsert_fn = upsert_map[endpoint_key]
        saved = await upsert_fn(agent_id, rows)

        # -- Log sync --
        if endpoint_key in ONCE_PER_DAY_NO_DATE:
            await self.repo.log_sync(agent_id, endpoint_key, today, saved)
        elif endpoint_key in REQUIRES_DATE and data_date:
            await self.repo.log_sync(agent_id, endpoint_key, data_date, saved)

        logger.info("Hoàn tất %s: tải=%d, tổng=%d, lưu=%d dòng",
                     endpoint_key, len(rows), total_count, saved)

        return {
            "endpoint": endpoint_key,
            "fetched": len(rows),
            "total": total_count,
            "saved": saved,
            "data_date": data_date,
            "total_data": total_data,
        }

    async def sync_all(
        self,
        base_url: str,
        cookies: str,
        agent_id: int,
        *,
        data_date: str | None = None,
        max_pages: int = 0,
        endpoints: list[str] | None = None,
        on_progress: Callable[[dict], None] | None = None,
    ) -> dict:
        """Sync all (or selected) endpoints.

        Args:
            on_progress: Async/sync callback called after each endpoint completes.
                         Receives {"type": "progress", "endpoint": ..., "result": ...}
                         or {"type": "done", ...} when all complete.
        """
        headers = {**DEFAULT_HEADERS, "Cookie": cookies.strip()}
        logger.info(
            "Bắt đầu đồng bộ: url=%s, cookie=%d ký tự",
            base_url, len(cookies),
        )
        target_endpoints = endpoints or list(ENDPOINTS.keys())

        results = {}
        skipped = []
        errors = []
        started_at = datetime.now(UTC)

        async def _notify(msg: dict) -> None:
            if on_progress is None:
                return
            ret = on_progress(msg)
            if asyncio.iscoroutine(ret) or asyncio.isfuture(ret):
                await ret

        # Notify start
        await _notify({
            "type": "start",
            "total": len(target_endpoints),
            "endpoints": target_endpoints,
        })

        async with httpx.AsyncClient(
            base_url=base_url,
            headers=headers,
            timeout=httpx.Timeout(30.0, connect=10.0),
            follow_redirects=False,
        ) as client:
            for idx, key in enumerate(target_endpoints):
                if key not in ENDPOINTS:
                    result = {"endpoint": key, "error": f"Endpoint không hợp lệ: {key}"}
                    results[key] = result
                    await _notify({"type": "progress", "index": idx, "endpoint": key, "result": result})
                    continue
                try:
                    # Detail callback for per-page/per-save progress
                    async def _on_detail(msg: dict, _key=key, _idx=idx) -> None:
                        await _notify({"type": "detail", "index": _idx, "endpoint": _key, **msg})

                    result = await self.sync_endpoint(
                        client, key, agent_id,
                        data_date=data_date,
                        max_pages=max_pages,
                        on_detail=_on_detail,
                    )
                    results[key] = result

                    if result.get("skipped"):
                        skipped.append(key)
                    if result.get("error"):
                        errors.append(key)

                    await _notify({"type": "progress", "index": idx, "endpoint": key, "result": result})

                    # If cookie expired -> stop all remaining
                    if result.get("error") and "cookie" in str(result["error"]).lower():
                        logger.error("Cookie hết hạn, dừng đồng bộ toàn bộ")
                        for remaining in target_endpoints[idx + 1:]:
                            skip_result = {
                                "endpoint": remaining,
                                "skipped": True,
                                "reason": "Dừng lại do cookie hết hạn",
                            }
                            results[remaining] = skip_result
                            skipped.append(remaining)
                            await _notify({"type": "progress", "index": target_endpoints.index(remaining), "endpoint": remaining, "result": skip_result})
                        break
                except Exception as e:
                    logger.exception("Lỗi đồng bộ %s", key)
                    result = {"endpoint": key, "error": str(e)}
                    results[key] = result
                    errors.append(key)
                    await _notify({"type": "progress", "index": idx, "endpoint": key, "result": result})

        finished_at = datetime.now(UTC)
        summary = {
            "agent_id": agent_id,
            "data_date": data_date,
            "started_at": started_at.isoformat(),
            "finished_at": finished_at.isoformat(),
            "duration_seconds": (finished_at - started_at).total_seconds(),
            "skipped": skipped,
            "errors": errors,
            "results": results,
        }

        await _notify({"type": "done", **summary})

        return summary
