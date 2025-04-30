import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import JSON, BigInteger, String, Integer, Boolean, DateTime, func
from typing import Optional
from datetime import datetime

# Настройка асинхронного движка
db_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "database")
os.makedirs(db_dir, exist_ok=True)
db_path = os.path.join(db_dir, "bot.db")

# Асинхронный движок для SQLite
engine = create_async_engine(
    f"sqlite+aiosqlite:///{db_path}",
    connect_args={"check_same_thread": False}
)

# Асинхронная сессия
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

async def init_db():
    """Создание таблиц при старте"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)