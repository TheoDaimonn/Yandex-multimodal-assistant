import json
import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings


load_dotenv(override=True)

DB_URL = os.getenv("DB_URL")

class Config(BaseSettings):
    TG_API_TOKEN: str


config = Config()
