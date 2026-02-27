from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ReportLottery(Base):
    """Báo cáo xổ số — synced from /agent/reportLottery.html"""

    __tablename__ = "report_lottery"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(Integer, index=True)
    username: Mapped[str] = mapped_column(String(100), index=True)
    user_parent_format: Mapped[str | None] = mapped_column(String(100))
    bet_count: Mapped[str | None] = mapped_column(String(50))
    bet_amount: Mapped[str | None] = mapped_column(String(50))
    valid_amount: Mapped[str | None] = mapped_column(String(50))
    rebate_amount: Mapped[str | None] = mapped_column(String(50))
    result: Mapped[str | None] = mapped_column(String(100))
    win_lose: Mapped[str | None] = mapped_column(String(50))
    prize: Mapped[str | None] = mapped_column(String(50))
    lottery_name: Mapped[str | None] = mapped_column(String(200))
    synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ReportFunds(Base):
    """Báo cáo tài chính — synced from /agent/reportFunds.html"""

    __tablename__ = "report_funds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(Integer, index=True)
    username: Mapped[str] = mapped_column(String(100), index=True)
    user_parent_format: Mapped[str | None] = mapped_column(String(100))
    deposit_count: Mapped[str | None] = mapped_column(String(50))
    deposit_amount: Mapped[str | None] = mapped_column(String(50))
    withdrawal_count: Mapped[str | None] = mapped_column(String(50))
    withdrawal_amount: Mapped[str | None] = mapped_column(String(50))
    charge_fee: Mapped[str | None] = mapped_column(String(50))
    agent_commission: Mapped[str | None] = mapped_column(String(50))
    promotion: Mapped[str | None] = mapped_column(String(50))
    third_rebate: Mapped[str | None] = mapped_column(String(50))
    third_activity_amount: Mapped[str | None] = mapped_column(String(50))
    date: Mapped[str | None] = mapped_column(String(20), index=True)
    synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ReportProvider(Base):
    """Báo cáo nhà cung cấp game — synced from /agent/reportThirdGame.html"""

    __tablename__ = "report_provider"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(Integer, index=True)
    username: Mapped[str] = mapped_column(String(100), index=True)
    platform_id_name: Mapped[str | None] = mapped_column(String(200))
    t_bet_times: Mapped[str | None] = mapped_column(String(50))
    t_bet_amount: Mapped[str | None] = mapped_column(String(50))
    t_turnover: Mapped[str | None] = mapped_column(String(50))
    t_prize: Mapped[str | None] = mapped_column(String(50))
    t_win_lose: Mapped[str | None] = mapped_column(String(50))
    report_date: Mapped[str | None] = mapped_column(String(20), index=True)
    synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
