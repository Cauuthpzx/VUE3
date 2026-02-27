from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Bet(Base):
    """Đơn cược xổ số — synced from /agent/bet.html"""

    __tablename__ = "bets"
    __table_args__ = (
        UniqueConstraint("agent_id", "serial_no", name="uq_bets_serial"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(Integer, index=True)
    serial_no: Mapped[str] = mapped_column(String(200), index=True)
    username: Mapped[str] = mapped_column(String(100), index=True)
    create_time: Mapped[str | None] = mapped_column(String(50))
    lottery_name: Mapped[str | None] = mapped_column(String(200))
    play_type_name: Mapped[str | None] = mapped_column(String(200))
    play_name: Mapped[str | None] = mapped_column(String(200))
    issue: Mapped[str | None] = mapped_column(String(100))
    content: Mapped[str | None] = mapped_column(Text)
    money: Mapped[str | None] = mapped_column(String(50))
    rebate_amount: Mapped[str | None] = mapped_column(String(50))
    result: Mapped[str | None] = mapped_column(String(100))
    status_text: Mapped[str | None] = mapped_column(String(100))
    synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class BetThirdParty(Base):
    """Đơn cược bên thứ 3 — synced from /agent/betOrder.html"""

    __tablename__ = "bet_third_party"
    __table_args__ = (
        UniqueConstraint("agent_id", "serial_no", name="uq_bet_third_serial"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(Integer, index=True)
    serial_no: Mapped[str] = mapped_column(String(250), index=True)
    platform_id_name: Mapped[str | None] = mapped_column(String(200))
    platform_username: Mapped[str | None] = mapped_column(String(200))
    c_name: Mapped[str | None] = mapped_column(String(200))
    game_name: Mapped[str | None] = mapped_column(String(200))
    bet_amount: Mapped[str | None] = mapped_column(String(50))
    turnover: Mapped[str | None] = mapped_column(String(50))
    prize: Mapped[str | None] = mapped_column(String(50))
    win_lose: Mapped[str | None] = mapped_column(String(50))
    bet_time: Mapped[str | None] = mapped_column(String(50))
    synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
