from sqlalchemy import Column, Integer, Boolean, String, JSON, ForeignKey, BigInteger
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base
from src.telegram_bot.app.models.Session import Session
from src.telegram_bot.app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String(255))
    is_admin: Mapped[bool] = mapped_column(default=False)

    sessions: Mapped[list["Session"]] = relationship("Session", back_populates="user")