from typing import Optional

from sqlalchemy import Column, Integer, Boolean, String, JSON, ForeignKey, BigInteger, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
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

    # Дополнительные поля
    psychological_profile: Mapped[Optional[str]] = mapped_column(String)