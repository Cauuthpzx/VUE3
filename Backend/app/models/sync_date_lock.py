from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SyncDateLock(Base):
    """Tracks per-date lock status for each endpoint after VerifySync confirms data integrity."""

    __tablename__ = "sync_date_lock"
    __table_args__ = (
        UniqueConstraint("agent_id", "endpoint_key", "date", name="uq_sync_date_lock"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(Integer, index=True)
    endpoint_key: Mapped[str] = mapped_column(String(50), index=True)
    date: Mapped[str] = mapped_column(String(10), index=True)  # "YYYY-MM-DD"
    record_count: Mapped[int] = mapped_column(Integer, default=0)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verify_method: Mapped[str | None] = mapped_column(String(20), nullable=True)  # "count" or "sample"
    synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
