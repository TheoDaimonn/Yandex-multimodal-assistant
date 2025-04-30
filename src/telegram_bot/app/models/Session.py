from sqlalchemy import Column, Integer, Boolean, String, JSON, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.declarative import declarative_base
from src.telegram_bot.app.models.User import User
from src.telegram_bot.app.database import Base
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    history: Mapped[dict | None] = mapped_column(JSON)
    summary: Mapped[str | None] = mapped_column(String)

    user: Mapped["User"] = relationship("User", back_populates="sessions")