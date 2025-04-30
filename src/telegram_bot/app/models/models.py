from typing import Optional, List

from sqlalchemy import Integer, String, JSON, BigInteger, DateTime, func
from sqlalchemy.ext.mutable import MutableList

from src.telegram_bot.app.database import Base

from sqlalchemy.orm import Mapped, mapped_column


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(255))

    # Поля для хранения переписки и контекста
    message_count: Mapped[int] = mapped_column(Integer, default=0)
    last_summary: Mapped[Optional[str]] = mapped_column(String)
    last_activity: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    current_messages:  Mapped[List[str]] = mapped_column(MutableList.as_mutable(JSON), default=list)

    # Дополнительные поля
    psychological_profile: Mapped[Optional[str]] = mapped_column(String)
