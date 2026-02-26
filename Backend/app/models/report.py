from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ReportLottery(Base):
    """Báo cáo xổ số — synced from /agent/reportLottery.html"""

    __tablename__ = "report_lottery"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(Integer, index=True)
    username: Mapped[str] = mapped_column(String(100), index=True)
    user_parent_format: Mapped[str | None] = mapped_column(String(100))
    bet_count: Mapped[int] = mapped_column(Integer, default=0)
    bet_amount: Mapped[float] = mapped_column(Numeric(16, 2), default=0)
    valid_amount: Mapped[float] = mapped_column(Numeric(16, 2), default=0)
    rebate_amount: Mapped[float] = mapped_column(Numeric(16, 2), default=0)
    result: Mapped[str | None] = mapped_column(String(100))
    win_lose: Mapped[float] = mapped_column(Numeric(16, 2), default=0)
    prize: Mapped[float] = mapped_column(Numeric(16, 2), default=0)
    lottery_name: Mapped[str | None] = mapped_column(String(200))
    report_date: Mapped[str | None] = mapped_column(String(20), index=True)
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
    deposit_count: Mapped[int] = mapped_column(Integer, default=0)
    deposit_amount: Mapped[float] = mapped_column(Numeric(16, 2), default=0)
    withdrawal_count: Mapped[int] = mapped_column(Integer, default=0)
    withdrawal_amount: Mapped[float] = mapped_column(Numeric(16, 2), default=0)
    charge_fee: Mapped[float] = mapped_column(Numeric(16, 2), default=0)
    agent_commission: Mapped[float] = mapped_column(Numeric(16, 2), default=0)
    promotion: Mapped[float] = mapped_column(Numeric(16, 2), default=0)
    third_rebate: Mapped[float] = mapped_column(Numeric(16, 2), default=0)
    third_activity_amount: Mapped[float] = mapped_column(Numeric(16, 2), default=0)
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
    t_bet_times: Mapped[int] = mapped_column(Integer, default=0)
    t_bet_amount: Mapped[float] = mapped_column(Numeric(16, 2), default=0)
    t_turnover: Mapped[float] = mapped_column(Numeric(16, 2), default=0)
    t_prize: Mapped[float] = mapped_column(Numeric(16, 2), default=0)
    t_win_lose: Mapped[float] = mapped_column(Numeric(16, 2), default=0)
    report_date: Mapped[str | None] = mapped_column(String(20), index=True)
    synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
