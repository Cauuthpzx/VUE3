from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SyncLog(Base):
    """Tracks which endpoint+date has been synced to enforce once-per-day rule."""

    __tablename__ = "sync_log"
    __table_args__ = (
        UniqueConstraint("agent_id", "endpoint_key", "sync_date", name="uq_sync_log"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(Integer, index=True)
    endpoint_key: Mapped[str] = mapped_column(String(50), index=True)
    sync_date: Mapped[str] = mapped_column(String(21), index=True)
    record_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
