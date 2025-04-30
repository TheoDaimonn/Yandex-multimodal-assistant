import os

from dotenv import load_dotenv
from sqlalchemy.orm import DeclarativeBase

import os
from sqlalchemy import create_engine

# Путь к базе данных
db_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "database")
os.makedirs(db_dir, exist_ok=True)
db_path = os.path.join(db_dir, "bot.db")

# Создание движка
engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})

load_dotenv(override=True)


class Base(DeclarativeBase):
    __abstract__ = True
