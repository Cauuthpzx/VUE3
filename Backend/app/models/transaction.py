from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Deposit(Base):
    """Nạp rút tiền — synced from /agent/depositAndWithdrawal.html"""

    __tablename__ = "deposits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(Integer, index=True)
    username: Mapped[str] = mapped_column(String(100), index=True)
    user_parent_format: Mapped[str | None] = mapped_column(String(100))
    amount: Mapped[str | None] = mapped_column(String(50))
    type: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[str | None] = mapped_column(String(50))
    create_time: Mapped[str | None] = mapped_column(String(50))
    synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Withdrawal(Base):
    """Lịch sử rút tiền — synced from /agent/withdrawalsRecord.html"""

    __tablename__ = "withdrawals"
    __table_args__ = (
        UniqueConstraint("agent_id", "serial_no", name="uq_withdrawals_serial"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(Integer, index=True)
    serial_no: Mapped[str] = mapped_column(String(200), index=True)
    create_time: Mapped[str | None] = mapped_column(String(50))
    username: Mapped[str] = mapped_column(String(100), index=True)
    user_parent_format: Mapped[str | None] = mapped_column(String(100))
    amount: Mapped[str | None] = mapped_column(String(50))
    user_fee: Mapped[str | None] = mapped_column(String(50))
    true_amount: Mapped[str | None] = mapped_column(String(50))
    status_format: Mapped[str | None] = mapped_column(String(50))
    synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
