from sqlalchemy import Column, Integer, Boolean, String, JSON, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
from src.telegram_bot.app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String(255))
    is_admin: Mapped[bool] = mapped_column(default=False)

    sessions: Mapped[list["Session"]] = relationship("Session", back_populates="users")


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    history: Mapped[dict | None] = mapped_column(JSON)
    summary: Mapped[str | None] = mapped_column(String)

    user: Mapped["User"] = relationship("User", back_populates="sessions")