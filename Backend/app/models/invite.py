from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Invite(Base):
    """Mã giới thiệu — synced from /agent/inviteList.html"""

    __tablename__ = "invites"
    __table_args__ = (
        UniqueConstraint("agent_id", "source_id", name="uq_invites_source"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(Integer, index=True)
    source_id: Mapped[int | None] = mapped_column(Integer, index=True)
    invite_code: Mapped[str] = mapped_column(String(100), index=True)
    user_type: Mapped[str | None] = mapped_column(String(50))
    reg_count: Mapped[int] = mapped_column(Integer, default=0)
    scope_reg_count: Mapped[int] = mapped_column(Integer, default=0)
    recharge_count: Mapped[int] = mapped_column(Integer, default=0)
    first_recharge_count: Mapped[int] = mapped_column(Integer, default=0)
    register_recharge_count: Mapped[int] = mapped_column(Integer, default=0)
    remark: Mapped[str | None] = mapped_column(Text)
    create_time: Mapped[str | None] = mapped_column(String(50))
    synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
