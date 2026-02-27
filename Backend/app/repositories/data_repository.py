from sqlalchemy import Numeric, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bet import Bet, BetThirdParty
from app.models.invite import Invite
from app.models.member import Member
from app.models.report import ReportFunds, ReportLottery, ReportProvider
from app.models.transaction import Deposit, Withdrawal

MODEL_MAP = {
    "members": Member,
    "invites": Invite,
    "bets": Bet,
    "bet_third_party": BetThirdParty,
    "deposits": Deposit,
    "withdrawals": Withdrawal,
    "report_lottery": ReportLottery,
    "report_funds": ReportFunds,
    "report_provider": ReportProvider,
}


def _sum_str(col):
    """Sum a string column by casting to Numeric first."""
    return func.sum(cast(col, Numeric(16, 4)))


class DataRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_paginated(
        self,
        model_key: str,
        agent_id: int,
        page: int = 1,
        limit: int = 10,
    ) -> tuple[list, int]:
        model = MODEL_MAP[model_key]
        offset = (page - 1) * limit

        count_stmt = select(func.count()).select_from(model).where(
            model.agent_id == agent_id
        )
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0

        data_stmt = (
            select(model)
            .where(model.agent_id == agent_id)
            .offset(offset)
            .limit(limit)
            .order_by(model.id.desc())
        )
        data_result = await self.db.execute(data_stmt)
        rows = list(data_result.scalars().all())

        return rows, total

    async def get_report_lottery_totals(self, agent_id: int) -> dict:
        model = ReportLottery
        stmt = select(
            _sum_str(model.bet_count).label("total_bet_count"),
            _sum_str(model.bet_amount).label("total_bet_amount"),
            _sum_str(model.valid_amount).label("total_valid_amount"),
            _sum_str(model.rebate_amount).label("total_rebate_amount"),
            _sum_str(model.win_lose).label("total_win_lose"),
            _sum_str(model.prize).label("total_prize"),
            func.count(func.distinct(model.username)).label("total_bet_number"),
        ).where(model.agent_id == agent_id)
        result = await self.db.execute(stmt)
        row = result.one()
        return {
            "total_bet_count": str(row.total_bet_count or 0),
            "total_bet_amount": str(row.total_bet_amount or 0),
            "total_valid_amount": str(row.total_valid_amount or 0),
            "total_rebate_amount": str(row.total_rebate_amount or 0),
            "total_result": str(row.total_win_lose or 0),
            "total_win_lose": str(row.total_win_lose or 0),
            "total_prize": str(row.total_prize or 0),
            "total_bet_number": row.total_bet_number or 0,
        }

    async def get_report_funds_totals(self, agent_id: int) -> dict:
        model = ReportFunds
        stmt = select(
            _sum_str(model.deposit_count).label("total_deposit_count"),
            _sum_str(model.deposit_amount).label("total_deposit_amount"),
            _sum_str(model.withdrawal_count).label("total_withdrawal_count"),
            _sum_str(model.withdrawal_amount).label("total_withdrawal_amount"),
            _sum_str(model.charge_fee).label("total_charge_fee"),
            _sum_str(model.agent_commission).label("total_agent_commission"),
            _sum_str(model.promotion).label("total_promotion"),
            _sum_str(model.third_rebate).label("total_third_rebate"),
            _sum_str(model.third_activity_amount).label("third_activity_amount"),
        ).where(model.agent_id == agent_id)
        result = await self.db.execute(stmt)
        row = result.one()
        return {
            "total_deposit_count": str(row.total_deposit_count or 0),
            "total_deposit_amount": str(row.total_deposit_amount or 0),
            "total_withdrawal_count": str(row.total_withdrawal_count or 0),
            "total_withdrawal_amount": str(row.total_withdrawal_amount or 0),
            "total_charge_fee": str(row.total_charge_fee or 0),
            "total_agent_commission": str(row.total_agent_commission or 0),
            "total_promotion": str(row.total_promotion or 0),
            "total_third_rebate": str(row.total_third_rebate or 0),
            "third_activity_amount": str(row.third_activity_amount or 0),
        }

    async def get_report_provider_totals(self, agent_id: int) -> dict:
        model = ReportProvider
        stmt = select(
            _sum_str(model.t_bet_times).label("total_bet_times"),
            _sum_str(model.t_bet_amount).label("total_bet_amount"),
            _sum_str(model.t_turnover).label("total_turnover"),
            _sum_str(model.t_prize).label("total_prize"),
            _sum_str(model.t_win_lose).label("total_win_lose"),
            func.count(func.distinct(model.username)).label("total_bet_number"),
        ).where(model.agent_id == agent_id)
        result = await self.db.execute(stmt)
        row = result.one()
        return {
            "total_bet_times": str(row.total_bet_times or 0),
            "total_bet_amount": str(row.total_bet_amount or 0),
            "total_turnover": str(row.total_turnover or 0),
            "total_prize": str(row.total_prize or 0),
            "total_win_lose": str(row.total_win_lose or 0),
            "total_bet_number": row.total_bet_number or 0,
        }
