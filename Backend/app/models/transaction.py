from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Deposit(Base):
    """Nạp rút tiền — synced from /agent/depositAndWithdrawal.html"""

    __tablename__ = "deposits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(Integer, index=True)
    username: Mapped[str] = mapped_column(String(100), index=True)
    user_parent_format: Mapped[str | None] = mapped_column(String(100))
    amount: Mapped[float] = mapped_column(Numeric(16, 2), default=0)
    type: Mapped[int] = mapped_column(Integer, default=1)
    type_text: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[int] = mapped_column(Integer, default=0)
    status_text: Mapped[str | None] = mapped_column(String(50))
    create_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
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

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(Integer, index=True)
    serial_no: Mapped[str] = mapped_column(String(200), index=True)
    create_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    username: Mapped[str] = mapped_column(String(100), index=True)
    user_parent_format: Mapped[str | None] = mapped_column(String(100))
    amount: Mapped[float] = mapped_column(Numeric(16, 2), default=0)
    user_fee: Mapped[float] = mapped_column(Numeric(16, 2), default=0)
    true_amount: Mapped[float] = mapped_column(Numeric(16, 2), default=0)
    status: Mapped[int] = mapped_column(Integer, default=0)
    status_format: Mapped[str | None] = mapped_column(String(50))
    synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
