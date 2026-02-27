"""sync_repository.py — Bulk upsert data from upstream API.

Tối ưu dựa trên reference (server/fetch_data.py):
  - Dùng raw SQL INSERT ... ON CONFLICT DO UPDATE (cực nhanh)
  - Batch insert qua executemany (không loop từng row)
  - Members/Invites: upsert trên source_id (API field "id")
  - Bets/BetThirdParty/Withdrawals: upsert trên serial_no
  - Deposits/Reports: insert only (không có unique key tự nhiên)
"""

import logging

from datetime import UTC, datetime

from sqlalchemy import delete, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bet import Bet, BetThirdParty
from app.models.invite import Invite
from app.models.member import Member
from app.models.report import ReportFunds, ReportLottery, ReportProvider
from app.models.sync_date_lock import SyncDateLock
from app.models.sync_log import SyncLog
from app.models.transaction import Deposit, Withdrawal

logger = logging.getLogger(__name__)

# Fields to exclude when mapping API data → model columns
EXCLUDED_FIELDS = {"id", "agent_id", "source_id", "synced_at", "created_at", "updated_at"}


def _filter_row(model_class, row: dict) -> dict:
    """Filter API row to only include valid model columns."""
    valid_columns = {c.name for c in model_class.__table__.columns} - EXCLUDED_FIELDS
    return {k: v for k, v in row.items() if k in valid_columns}


def _s(val) -> str | None:
    """Convert any value to str for String columns (asyncpg requires exact type match)."""
    if val is None:
        return None
    return str(val)


class SyncRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── Members — ON CONFLICT (agent_id, source_id) ──────────────
    async def upsert_members(self, agent_id: int, rows: list[dict]) -> int:
        if not rows:
            return 0

        sql = text("""
            INSERT INTO members
                (agent_id, source_id, username, type_format, parent_user, money,
                 deposit_count, withdrawal_count, deposit_amount, withdrawal_amount,
                 login_time, register_time, status_format, synced_at, created_at)
            VALUES
                (:agent_id, :source_id, :username, :type_format, :parent_user, :money,
                 :deposit_count, :withdrawal_count, :deposit_amount, :withdrawal_amount,
                 :login_time, :register_time, :status_format, NOW(), NOW())
            ON CONFLICT ON CONSTRAINT uq_members_source DO UPDATE SET
                money = EXCLUDED.money,
                deposit_count = EXCLUDED.deposit_count,
                withdrawal_count = EXCLUDED.withdrawal_count,
                deposit_amount = EXCLUDED.deposit_amount,
                withdrawal_amount = EXCLUDED.withdrawal_amount,
                login_time = EXCLUDED.login_time,
                status_format = EXCLUDED.status_format,
                synced_at = NOW(),
                updated_at = NOW()
        """)

        params = []
        for row in rows:
            source_id = row.get("id")
            if not source_id:
                continue
            filtered = _filter_row(Member, row)
            params.append({
                "agent_id": agent_id,
                "source_id": int(source_id),
                "username": filtered.get("username", ""),
                "type_format": _s(filtered.get("type_format")),
                "parent_user": _s(filtered.get("parent_user")),
                "money": _s(filtered.get("money")),
                "deposit_count": int(filtered.get("deposit_count", 0) or 0),
                "withdrawal_count": int(filtered.get("withdrawal_count", 0) or 0),
                "deposit_amount": _s(filtered.get("deposit_amount")),
                "withdrawal_amount": _s(filtered.get("withdrawal_amount")),
                "login_time": _s(filtered.get("login_time")),
                "register_time": _s(filtered.get("register_time")),
                "status_format": _s(filtered.get("status_format")),
            })

        if params:
            await self.db.execute(sql, params)
            await self.db.commit()

        logger.info("Members: %d rows upserted", len(params))
        return len(params)

    # ── Invites — ON CONFLICT (agent_id, source_id) ──────────────
    async def upsert_invites(self, agent_id: int, rows: list[dict]) -> int:
        if not rows:
            return 0

        sql = text("""
            INSERT INTO invites
                (agent_id, source_id, invite_code, user_type, reg_count,
                 scope_reg_count, recharge_count, first_recharge_count,
                 register_recharge_count, remark, create_time, synced_at, created_at)
            VALUES
                (:agent_id, :source_id, :invite_code, :user_type, :reg_count,
                 :scope_reg_count, :recharge_count, :first_recharge_count,
                 :register_recharge_count, :remark, :create_time, NOW(), NOW())
            ON CONFLICT ON CONSTRAINT uq_invites_source DO UPDATE SET
                reg_count = EXCLUDED.reg_count,
                scope_reg_count = EXCLUDED.scope_reg_count,
                recharge_count = EXCLUDED.recharge_count,
                first_recharge_count = EXCLUDED.first_recharge_count,
                register_recharge_count = EXCLUDED.register_recharge_count,
                synced_at = NOW(),
                updated_at = NOW()
        """)

        params = []
        for row in rows:
            source_id = row.get("id")
            if not source_id:
                continue
            filtered = _filter_row(Invite, row)
            params.append({
                "agent_id": agent_id,
                "source_id": int(source_id),
                "invite_code": filtered.get("invite_code", ""),
                "user_type": _s(filtered.get("user_type")),
                "reg_count": int(filtered.get("reg_count", 0) or 0),
                "scope_reg_count": int(filtered.get("scope_reg_count", 0) or 0),
                "recharge_count": int(filtered.get("recharge_count", 0) or 0),
                "first_recharge_count": int(filtered.get("first_recharge_count", 0) or 0),
                "register_recharge_count": int(filtered.get("register_recharge_count", 0) or 0),
                "remark": _s(filtered.get("remark", "")),
                "create_time": _s(filtered.get("create_time")),
            })

        if params:
            await self.db.execute(sql, params)
            await self.db.commit()

        logger.info("Invites: %d rows upserted", len(params))
        return len(params)

    # ── Bets — ON CONFLICT (agent_id, serial_no) ─────────────────
    async def upsert_bets(self, agent_id: int, rows: list[dict]) -> int:
        if not rows:
            return 0

        sql = text("""
            INSERT INTO bets
                (agent_id, serial_no, username, create_time, lottery_name,
                 play_type_name, play_name, issue, content, money,
                 rebate_amount, result, status_text, synced_at, created_at)
            VALUES
                (:agent_id, :serial_no, :username, :create_time, :lottery_name,
                 :play_type_name, :play_name, :issue, :content, :money,
                 :rebate_amount, :result, :status_text, NOW(), NOW())
            ON CONFLICT ON CONSTRAINT uq_bets_serial DO UPDATE SET
                result = EXCLUDED.result,
                status_text = EXCLUDED.status_text,
                synced_at = NOW(),
                updated_at = NOW()
        """)

        params = []
        for row in rows:
            serial_no = row.get("serial_no")
            if not serial_no:
                continue
            filtered = _filter_row(Bet, row)
            params.append({
                "agent_id": agent_id,
                "serial_no": str(serial_no),
                "username": filtered.get("username", ""),
                "create_time": _s(filtered.get("create_time")),
                "lottery_name": _s(filtered.get("lottery_name")),
                "play_type_name": _s(filtered.get("play_type_name")),
                "play_name": _s(filtered.get("play_name")),
                "issue": _s(filtered.get("issue")),
                "content": _s(filtered.get("content")),
                "money": _s(filtered.get("money")),
                "rebate_amount": _s(filtered.get("rebate_amount")),
                "result": _s(filtered.get("result")),
                "status_text": _s(filtered.get("status_text")),
            })

        if params:
            await self.db.execute(sql, params)
            await self.db.commit()

        logger.info("Bets: %d rows upserted", len(params))
        return len(params)

    # ── Bets third-party — ON CONFLICT (agent_id, serial_no) ─────
    async def upsert_bet_third_party(self, agent_id: int, rows: list[dict]) -> int:
        if not rows:
            return 0

        sql = text("""
            INSERT INTO bet_third_party
                (agent_id, serial_no, platform_id_name, platform_username,
                 c_name, game_name, bet_amount, turnover, prize, win_lose,
                 bet_time, synced_at, created_at)
            VALUES
                (:agent_id, :serial_no, :platform_id_name, :platform_username,
                 :c_name, :game_name, :bet_amount, :turnover, :prize, :win_lose,
                 :bet_time, NOW(), NOW())
            ON CONFLICT ON CONSTRAINT uq_bet_third_serial DO UPDATE SET
                prize = EXCLUDED.prize,
                win_lose = EXCLUDED.win_lose,
                synced_at = NOW(),
                updated_at = NOW()
        """)

        params = []
        for row in rows:
            serial_no = row.get("serial_no")
            if not serial_no:
                continue
            filtered = _filter_row(BetThirdParty, row)
            params.append({
                "agent_id": agent_id,
                "serial_no": str(serial_no),
                "platform_id_name": _s(filtered.get("platform_id_name")),
                "platform_username": _s(filtered.get("platform_username")),
                "c_name": _s(filtered.get("c_name")),
                "game_name": _s(filtered.get("game_name")),
                "bet_amount": _s(filtered.get("bet_amount")),
                "turnover": _s(filtered.get("turnover")),
                "prize": _s(filtered.get("prize")),
                "win_lose": _s(filtered.get("win_lose")),
                "bet_time": _s(filtered.get("bet_time")),
            })

        if params:
            await self.db.execute(sql, params)
            await self.db.commit()

        logger.info("BetThirdParty: %d rows upserted", len(params))
        return len(params)

    # ── Deposits — INSERT only (no unique key) ───────────────────
    async def upsert_deposits(self, agent_id: int, rows: list[dict]) -> int:
        if not rows:
            return 0

        sql = text("""
            INSERT INTO deposits
                (agent_id, username, user_parent_format, amount, type, status,
                 create_time, synced_at, created_at)
            VALUES
                (:agent_id, :username, :user_parent_format, :amount, :type, :status,
                 :create_time, NOW(), NOW())
        """)

        params = []
        for row in rows:
            filtered = _filter_row(Deposit, row)
            if not filtered.get("username"):
                continue
            params.append({
                "agent_id": agent_id,
                "username": filtered.get("username", ""),
                "user_parent_format": _s(filtered.get("user_parent_format")),
                "amount": _s(filtered.get("amount")),
                "type": _s(filtered.get("type")),
                "status": _s(filtered.get("status")),
                "create_time": _s(filtered.get("create_time")),
            })

        if params:
            await self.db.execute(sql, params)
            await self.db.commit()

        logger.info("Deposits: %d rows inserted", len(params))
        return len(params)

    # ── Withdrawals — ON CONFLICT (agent_id, serial_no) ──────────
    async def upsert_withdrawals(self, agent_id: int, rows: list[dict]) -> int:
        if not rows:
            return 0

        sql = text("""
            INSERT INTO withdrawals
                (agent_id, serial_no, username, user_parent_format,
                 amount, user_fee, true_amount, status_format, create_time,
                 synced_at, created_at)
            VALUES
                (:agent_id, :serial_no, :username, :user_parent_format,
                 :amount, :user_fee, :true_amount, :status_format, :create_time,
                 NOW(), NOW())
            ON CONFLICT ON CONSTRAINT uq_withdrawals_serial DO UPDATE SET
                status_format = EXCLUDED.status_format,
                synced_at = NOW(),
                updated_at = NOW()
        """)

        params = []
        for row in rows:
            serial_no = row.get("serial_no")
            if not serial_no:
                continue
            filtered = _filter_row(Withdrawal, row)
            params.append({
                "agent_id": agent_id,
                "serial_no": str(serial_no),
                "username": filtered.get("username", ""),
                "user_parent_format": _s(filtered.get("user_parent_format")),
                "amount": _s(filtered.get("amount")),
                "user_fee": _s(filtered.get("user_fee")),
                "true_amount": _s(filtered.get("true_amount")),
                "status_format": _s(filtered.get("status_format")),
                "create_time": _s(filtered.get("create_time")),
            })

        if params:
            await self.db.execute(sql, params)
            await self.db.commit()

        logger.info("Withdrawals: %d rows upserted", len(params))
        return len(params)

    # ── Report Lottery — INSERT only ─────────────────────────────
    async def upsert_report_lottery(self, agent_id: int, rows: list[dict]) -> int:
        if not rows:
            return 0

        sql = text("""
            INSERT INTO report_lottery
                (agent_id, username, user_parent_format, lottery_name,
                 bet_count, bet_amount, valid_amount, rebate_amount,
                 result, win_lose, prize, synced_at, created_at)
            VALUES
                (:agent_id, :username, :user_parent_format, :lottery_name,
                 :bet_count, :bet_amount, :valid_amount, :rebate_amount,
                 :result, :win_lose, :prize, NOW(), NOW())
        """)

        params = []
        for row in rows:
            filtered = _filter_row(ReportLottery, row)
            if not filtered.get("username"):
                continue
            params.append({
                "agent_id": agent_id,
                "username": filtered.get("username", ""),
                "user_parent_format": _s(filtered.get("user_parent_format")),
                "lottery_name": _s(filtered.get("lottery_name")),
                "bet_count": _s(filtered.get("bet_count")),
                "bet_amount": _s(filtered.get("bet_amount")),
                "valid_amount": _s(filtered.get("valid_amount")),
                "rebate_amount": _s(filtered.get("rebate_amount")),
                "result": _s(filtered.get("result")),
                "win_lose": _s(filtered.get("win_lose")),
                "prize": _s(filtered.get("prize")),
            })

        if params:
            await self.db.execute(sql, params)
            await self.db.commit()

        logger.info("ReportLottery: %d rows inserted", len(params))
        return len(params)

    # ── Report Funds — INSERT only ───────────────────────────────
    async def upsert_report_funds(self, agent_id: int, rows: list[dict]) -> int:
        if not rows:
            return 0

        sql = text("""
            INSERT INTO report_funds
                (agent_id, username, user_parent_format,
                 deposit_count, deposit_amount, withdrawal_count, withdrawal_amount,
                 charge_fee, agent_commission, promotion, third_rebate,
                 third_activity_amount, date, synced_at, created_at)
            VALUES
                (:agent_id, :username, :user_parent_format,
                 :deposit_count, :deposit_amount, :withdrawal_count, :withdrawal_amount,
                 :charge_fee, :agent_commission, :promotion, :third_rebate,
                 :third_activity_amount, :date, NOW(), NOW())
        """)

        params = []
        for row in rows:
            filtered = _filter_row(ReportFunds, row)
            if not filtered.get("username"):
                continue
            params.append({
                "agent_id": agent_id,
                "username": filtered.get("username", ""),
                "user_parent_format": _s(filtered.get("user_parent_format")),
                "deposit_count": _s(filtered.get("deposit_count")),
                "deposit_amount": _s(filtered.get("deposit_amount")),
                "withdrawal_count": _s(filtered.get("withdrawal_count")),
                "withdrawal_amount": _s(filtered.get("withdrawal_amount")),
                "charge_fee": _s(filtered.get("charge_fee")),
                "agent_commission": _s(filtered.get("agent_commission")),
                "promotion": _s(filtered.get("promotion")),
                "third_rebate": _s(filtered.get("third_rebate")),
                "third_activity_amount": _s(filtered.get("third_activity_amount")),
                "date": _s(filtered.get("date")),
            })

        if params:
            await self.db.execute(sql, params)
            await self.db.commit()

        logger.info("ReportFunds: %d rows inserted", len(params))
        return len(params)

    # ── Report Provider — INSERT only ────────────────────────────
    async def upsert_report_provider(self, agent_id: int, rows: list[dict]) -> int:
        if not rows:
            return 0

        sql = text("""
            INSERT INTO report_provider
                (agent_id, username, platform_id_name, t_bet_times,
                 t_bet_amount, t_turnover, t_prize, t_win_lose,
                 report_date, synced_at, created_at)
            VALUES
                (:agent_id, :username, :platform_id_name, :t_bet_times,
                 :t_bet_amount, :t_turnover, :t_prize, :t_win_lose,
                 :report_date, NOW(), NOW())
        """)

        params = []
        for row in rows:
            filtered = _filter_row(ReportProvider, row)
            if not filtered.get("username"):
                continue
            params.append({
                "agent_id": agent_id,
                "username": filtered.get("username", ""),
                "platform_id_name": _s(filtered.get("platform_id_name")),
                "t_bet_times": _s(filtered.get("t_bet_times")),
                "t_bet_amount": _s(filtered.get("t_bet_amount")),
                "t_turnover": _s(filtered.get("t_turnover")),
                "t_prize": _s(filtered.get("t_prize")),
                "t_win_lose": _s(filtered.get("t_win_lose")),
                "report_date": _s(filtered.get("report_date")),
            })

        if params:
            await self.db.execute(sql, params)
            await self.db.commit()

        logger.info("ReportProvider: %d rows inserted", len(params))
        return len(params)

    # ── Sync Log ─────────────────────────────────────────────────
    async def is_synced_today(self, agent_id: int, endpoint_key: str, sync_date: str) -> bool:
        stmt = select(SyncLog).where(
            SyncLog.agent_id == agent_id,
            SyncLog.endpoint_key == endpoint_key,
            SyncLog.sync_date == sync_date,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def log_sync(self, agent_id: int, endpoint_key: str, sync_date: str, record_count: int) -> None:
        log = SyncLog(
            agent_id=agent_id,
            endpoint_key=endpoint_key,
            sync_date=sync_date,
            record_count=record_count,
        )
        self.db.add(log)
        await self.db.commit()

    # ── Date Lock — get/upsert/lock per-date entries ────────────
    # Mapping: endpoint_key → (table_name, date_column, date_match_type)
    # date_match_type: "like" = LIKE 'YYYY-MM-DD%', "exact" = = 'YYYY-MM-DD'
    DATE_COL_MAP = {
        "bets": ("bets", "create_time", "like"),
        "bet_third_party": ("bet_third_party", "bet_time", "like"),
        "deposits": ("deposits", "create_time", "like"),
        "withdrawals": ("withdrawals", "create_time", "like"),
        "report_funds": ("report_funds", "date", "exact"),
        "report_provider": ("report_provider", "report_date", "exact"),
        "report_lottery": ("report_lottery", "created_at", "cast_date"),
    }

    async def get_locked_dates(self, agent_id: int, endpoint_key: str, dates: list[str]) -> set[str]:
        """Return set of dates that are already locked for this agent+endpoint."""
        if not dates:
            return set()
        stmt = select(SyncDateLock.date).where(
            SyncDateLock.agent_id == agent_id,
            SyncDateLock.endpoint_key == endpoint_key,
            SyncDateLock.date.in_(dates),
            SyncDateLock.is_locked.is_(True),
        )
        result = await self.db.execute(stmt)
        return {row[0] for row in result.fetchall()}

    async def upsert_date_entry(self, agent_id: int, endpoint_key: str, date: str, record_count: int) -> None:
        """Create or update a date entry after sync (not yet locked)."""
        sql = text("""
            INSERT INTO sync_date_lock (agent_id, endpoint_key, date, record_count, is_locked, synced_at, created_at)
            VALUES (:agent_id, :endpoint_key, :date, :record_count, false, NOW(), NOW())
            ON CONFLICT ON CONSTRAINT uq_sync_date_lock DO UPDATE SET
                record_count = :record_count,
                synced_at = NOW()
        """)
        await self.db.execute(sql, {
            "agent_id": agent_id,
            "endpoint_key": endpoint_key,
            "date": date,
            "record_count": record_count,
        })
        await self.db.commit()

    async def lock_date(self, agent_id: int, endpoint_key: str, date: str, method: str) -> None:
        """Mark a single date as locked after verification."""
        await self.lock_dates_batch(agent_id, endpoint_key, [date], method)

    async def lock_dates_batch(self, agent_id: int, endpoint_key: str, dates: list[str], method: str) -> None:
        """Mark multiple dates as locked in a single transaction."""
        now = datetime.now(UTC)
        for date in dates:
            stmt = select(SyncDateLock).where(
                SyncDateLock.agent_id == agent_id,
                SyncDateLock.endpoint_key == endpoint_key,
                SyncDateLock.date == date,
            )
            result = await self.db.execute(stmt)
            entry = result.scalar_one_or_none()
            if entry:
                entry.is_locked = True
                entry.verified_at = now
                entry.verify_method = method
        await self.db.commit()

    async def count_rows_for_date(self, agent_id: int, endpoint_key: str, date: str) -> int:
        """Count rows in DB for a specific date (used for verify)."""
        mapping = self.DATE_COL_MAP.get(endpoint_key)
        if not mapping:
            return 0
        table_name, date_col, match_type = mapping

        if match_type == "like":
            sql = text(f"SELECT COUNT(*) FROM {table_name} WHERE agent_id = :agent_id AND {date_col} LIKE :date_pattern")
            result = await self.db.execute(sql, {"agent_id": agent_id, "date_pattern": f"{date}%"})
        elif match_type == "exact":
            sql = text(f"SELECT COUNT(*) FROM {table_name} WHERE agent_id = :agent_id AND {date_col} = :date")
            result = await self.db.execute(sql, {"agent_id": agent_id, "date": date})
        elif match_type == "cast_date":
            sql = text(f"SELECT COUNT(*) FROM {table_name} WHERE agent_id = :agent_id AND CAST({date_col} AS DATE) = :date")
            result = await self.db.execute(sql, {"agent_id": agent_id, "date": date})
        else:
            return 0

        return result.scalar() or 0

    async def get_sample_serials(self, agent_id: int, endpoint_key: str, date: str, limit: int = 5) -> list[str]:
        """Get sample serial_no values for UPSERT tables (used for verify)."""
        serial_tables = {
            "bets": ("bets", "serial_no", "create_time"),
            "bet_third_party": ("bet_third_party", "serial_no", "bet_time"),
            "withdrawals": ("withdrawals", "serial_no", "create_time"),
        }
        mapping = serial_tables.get(endpoint_key)
        if not mapping:
            return []
        table_name, serial_col, date_col = mapping

        sql = text(
            f"SELECT {serial_col} FROM {table_name} "
            f"WHERE agent_id = :agent_id AND {date_col} LIKE :date_pattern "
            f"ORDER BY RANDOM() LIMIT :limit"
        )
        result = await self.db.execute(sql, {
            "agent_id": agent_id,
            "date_pattern": f"{date}%",
            "limit": limit,
        })
        return [row[0] for row in result.fetchall()]

    # ── Clear all data for re-sync ───────────────────────────────
    async def clear_all(self, agent_id: int) -> None:
        for model in [Member, Invite, Bet, BetThirdParty, Deposit, Withdrawal,
                       ReportLottery, ReportFunds, ReportProvider, SyncLog, SyncDateLock]:
            await self.db.execute(
                delete(model).where(model.agent_id == agent_id)
            )
        await self.db.commit()
