"""Upstream proxy — parallel fetch from all active agents.

Speed design:
- httpx.AsyncClient with connection pooling (keep-alive)
- asyncio.gather for parallel requests (latency = max, not sum)
- Each row tagged with _agent_name for the "Đại lý" column
"""

import asyncio
import logging
from datetime import UTC, datetime

import httpx
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import Agent
from app.services.agent_login_service import (
    AgentLoginService,
    cookie_dict_to_str,
    cookie_str_to_dict,
    decrypt_password,
)

logger = logging.getLogger(__name__)

_client_lock = asyncio.Lock()
_agent_cookie_locks: dict[int, asyncio.Lock] = {}  # Per-agent lock for cookie refresh


def _get_cookie_lock(agent_id: int) -> asyncio.Lock:
    """Get or create a lock for agent cookie operations (check + re-login)."""
    if agent_id not in _agent_cookie_locks:
        _agent_cookie_locks[agent_id] = asyncio.Lock()
    return _agent_cookie_locks[agent_id]

# Map frontend endpoint names → upstream URL paths
UPSTREAM_PATHS: dict[str, str] = {
    "members": "/agent/user.html",
    "invites": "/agent/inviteList.html",
    "bets": "/agent/bet.html",
    "bet-orders": "/agent/betOrder.html",
    "report-lottery": "/agent/reportLottery.html",
    "report-funds": "/agent/reportFunds.html",
    "report-third": "/agent/reportThirdGame.html",
    "deposits": "/agent/depositAndWithdrawal.html",
    "withdrawals": "/agent/withdrawalsRecord.html",
}

_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
)

# Default params per endpoint (required by upstream but not sent by frontend)
UPSTREAM_DEFAULTS: dict[str, dict] = {
    "bets": {"es": "1"},
    "bet-orders": {"es": "1"},
}

# Reusable client with connection pooling
_client: httpx.AsyncClient | None = None


async def get_client() -> httpx.AsyncClient:
    global _client
    if _client is not None and not _client.is_closed:
        return _client
    async with _client_lock:
        if _client is not None and not _client.is_closed:
            return _client
        _client = httpx.AsyncClient(
            timeout=30.0,
            verify=True,
            limits=httpx.Limits(max_connections=50, max_keepalive_connections=20),
            http2=True,
        )
    return _client


async def close_httpx_client() -> None:
    """Close the global httpx client. Called during application shutdown."""
    global _client
    if _client is not None and not _client.is_closed:
        await _client.aclose()
        _client = None


async def get_active_agents(
    db: AsyncSession, agent_id: int | None = None
) -> list[Agent]:
    stmt = select(Agent).where(Agent.is_active.is_(True))
    if agent_id and agent_id > 0:
        stmt = stmt.where(Agent.id == agent_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def _ensure_agent_cookie(agent: Agent, db: AsyncSession) -> None:
    """Kiểm tra cookie upstream còn sống không. Nếu hết hạn → auto re-login.

    Per-agent lock ngăn chặn nhiều request cùng re-login 1 agent đồng thời.
    """
    if not agent.password_enc:
        return

    lock = _get_cookie_lock(agent.id)
    async with lock:
        # Re-read agent from DB inside lock (cookie may have been refreshed by another task)
        await db.refresh(agent)

        cookies_dict = cookie_str_to_dict(agent.cookie or "")
        svc = AgentLoginService(agent.base_url)

        try:
            is_valid, msg = await asyncio.to_thread(svc.check_cookies_live, cookies_dict)
            if is_valid:
                return

            logger.warning("Agent %s cookie expired (%s) — re-logging in", agent.id, msg)
            plain_pw = decrypt_password(agent.password_enc)
            ok, login_msg, new_cookies = await asyncio.to_thread(
                svc.login, agent.username, plain_pw
            )

            if not ok:
                logger.warning("Agent %s re-login failed: %s", agent.id, login_msg)
                return

            new_cookie_str = cookie_dict_to_str(new_cookies)
            now = datetime.now(UTC)
            await db.execute(
                update(Agent)
                .where(Agent.id == agent.id)
                .values(cookie=new_cookie_str, last_login_at=now, updated_at=now)
            )
            await db.commit()
            await db.refresh(agent)
            logger.success("Agent %s re-login OK, cookie=%d ký tự", agent.id, len(new_cookie_str))
        finally:
            svc.close()


async def _fetch_one(
    client: httpx.AsyncClient,
    agent: Agent,
    upstream_path: str,
    form_data: dict,
) -> tuple[Agent, dict | None]:
    """Fetch from one upstream agent. Returns (agent, response_dict)."""
    headers = {
        "Cookie": agent.cookie or "",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": _USER_AGENT,
        "Referer": agent.base_url + upstream_path,
        "Origin": agent.base_url,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    url = agent.base_url + upstream_path
    try:
        resp = await client.post(url, data=form_data, headers=headers)
        data = resp.json()
        return agent, data
    except (httpx.HTTPError, ValueError) as e:
        logger.warning(
            "Agent %s (%s) fetch failed: %s", agent.id, agent.owner, e
        )
        return agent, None


async def fetch_all_agents(
    db: AsyncSession,
    endpoint: str,
    form_params: dict,
    agent_id: int | None = None,
) -> dict:
    """Fan-out to all active agents in parallel, merge results.

    Pass-through pagination: page/limit from frontend are forwarded
    directly to upstream so that upstream handles pagination with the
    correct total count. Each row is tagged with _agent_* metadata.
    """
    upstream_path = UPSTREAM_PATHS.get(endpoint)
    if not upstream_path:
        return {"code": 1, "msg": f"Unknown endpoint: {endpoint}", "data": [], "count": 0}

    agents = await get_active_agents(db, agent_id)
    if not agents:
        return {"code": 0, "msg": "No active agents", "data": [], "count": 0}

    # Pre-check cookies in parallel — tự động re-login nếu agent có password_enc và cookie hết hạn
    cookie_tasks = [
        _ensure_agent_cookie(ag, db)
        for ag in agents
        if ag.password_enc
    ]
    if cookie_tasks:
        await asyncio.gather(*cookie_tasks, return_exceptions=True)

    # Inject default params (e.g. es=1 for bet endpoints)
    defaults = UPSTREAM_DEFAULTS.get(endpoint, {})
    upstream_params = {**defaults, **form_params}

    # Pass-through page/limit to upstream — upstream handles pagination
    # and returns the correct total count (e.g. 50K+ members).
    if "page" not in upstream_params:
        upstream_params["page"] = "1"
    if "limit" not in upstream_params:
        upstream_params["limit"] = "10"

    client = await get_client()

    # Parallel fetch from all agents
    tasks = [_fetch_one(client, ag, upstream_path, upstream_params) for ag in agents]
    results = await asyncio.gather(*tasks)

    all_data: list[dict] = []
    total_count = 0

    for agent, result in results:
        if result is None:
            continue
        if result.get("code") == 0 and isinstance(result.get("data"), list):
            for row in result["data"]:
                row["_agent_id"] = agent.id
                row["_agent_name"] = agent.owner
                row["_agent_base_url"] = agent.base_url
            all_data.extend(result["data"])
            # Use upstream's count (total rows across all pages)
            total_count += int(result.get("count", len(result["data"])))

    return {"code": 0, "data": all_data, "count": total_count}


# ── Rebate-specific helpers (JSON API, not form-encoded) ──────────


async def _post_json(
    client: httpx.AsyncClient,
    agent: Agent,
    path: str,
    body: dict,
) -> dict | None:
    """POST JSON to an upstream agent path, return parsed response."""
    headers = {
        "Cookie": agent.cookie or "",
        "Content-Type": "application/json;charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": _USER_AGENT,
        "Referer": agent.base_url + "/agent/rebate",
        "Origin": agent.base_url,
    }
    url = agent.base_url + path
    try:
        resp = await client.post(url, json=body, headers=headers)
        return resp.json()
    except (httpx.HTTPError, ValueError) as e:
        logger.warning("Agent %s JSON %s failed: %s", agent.id, path, e)
        return None


async def fetch_rebate_init(
    db: AsyncSession,
    agent_id: int | None = None,
) -> dict:
    """Get lottery series + first series' games from first active agent."""
    agents = await get_active_agents(db, agent_id)
    if not agents:
        return {"series": [], "games": []}

    agent = agents[0]
    client = await get_client()

    # 1. Get all series
    res = await _post_json(client, agent, "/agent/getLottery", {"type": "init"})
    series: list = []
    if res and res.get("code") == 1:
        raw = res.get("data", [])
        series = raw if isinstance(raw, list) else []

    # 2. Get games for first series
    games: list = []
    if series:
        first_id = series[0].get("id") or series[0].get("series_id")
        if first_id:
            res2 = await _post_json(
                client,
                agent,
                "/agent/getLottery",
                {"type": "getLottery", "series_id": first_id},
            )
            if res2 and res2.get("code") == 1:
                raw2 = res2.get("data", [])
                games = raw2 if isinstance(raw2, list) else []

    return {"series": series, "games": games}


async def fetch_rebate_games(
    db: AsyncSession,
    series_id: str | int,
    agent_id: int | None = None,
) -> dict:
    """Get lottery games for a specific series."""
    agents = await get_active_agents(db, agent_id)
    if not agents:
        return {"games": []}

    agent = agents[0]
    client = await get_client()
    res = await _post_json(
        client,
        agent,
        "/agent/getLottery",
        {"type": "getLottery", "series_id": series_id},
    )
    games: list = []
    if res and res.get("code") == 1:
        raw = res.get("data", [])
        games = raw if isinstance(raw, list) else []

    return {"games": games}


async def fetch_rebate_panel(
    db: AsyncSession,
    lottery_id: str | int,
    series_id: str | int,
    agent_id: int | None = None,
) -> dict:
    """Get rebate odds panel for a specific lottery game."""
    agents = await get_active_agents(db, agent_id)
    if not agents:
        return {"code": 0, "data": [], "count": 0}

    agent = agents[0]
    client = await get_client()
    res = await _post_json(
        client,
        agent,
        "/agent/getRebateOddsPanel",
        {"lottery_id": lottery_id, "series_id": series_id},
    )

    if res and res.get("code") == 1:
        raw = res.get("data", {})
        rows = raw if isinstance(raw, list) else raw.get("list", [])
        for row in rows:
            row["_agent_name"] = agent.owner
        return {"code": 0, "data": rows, "count": len(rows)}

    return {"code": 0, "data": [], "count": 0}
