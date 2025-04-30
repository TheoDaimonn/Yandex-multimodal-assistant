import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

load_dotenv(override=True)

DB_URL = os.getenv("DB_URL")


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True


engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)