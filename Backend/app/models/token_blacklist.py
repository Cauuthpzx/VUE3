from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    token: Mapped[str] = mapped_column(String, unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
