from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Member(Base):
    """Hội viên thuộc cấp — synced from /agent/user.html"""

    __tablename__ = "members"
    __table_args__ = (
        UniqueConstraint("agent_id", "source_id", name="uq_members_source"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(Integer, index=True)
    source_id: Mapped[int | None] = mapped_column(Integer, index=True)
    username: Mapped[str] = mapped_column(String(100), index=True)
    type_format: Mapped[str | None] = mapped_column(String(50))
    parent_user: Mapped[str | None] = mapped_column(String(100))
    money: Mapped[str | None] = mapped_column(String(50))
    deposit_count: Mapped[int] = mapped_column(Integer, default=0)
    withdrawal_count: Mapped[int] = mapped_column(Integer, default=0)
    deposit_amount: Mapped[str | None] = mapped_column(String(50))
    withdrawal_amount: Mapped[str | None] = mapped_column(String(50))
    login_time: Mapped[str | None] = mapped_column(String(50))
    register_time: Mapped[str | None] = mapped_column(String(50))
    status_format: Mapped[str | None] = mapped_column(String(50))
    synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
