import json
import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings


load_dotenv(override=True)

DB_URL = os.getenv("DB_URL")

class Config(BaseSettings):
    TG_API_TOKEN: str
    ADMIN_USERNAME: str
    WIKI_AGENT_PARAMS: dict = {}


config = Config()

# ADMIN_ID = None
print(config.ADMIN_USERNAME)

WIKI_AGENT_PARAMS = json.loads(os.getenv("WIKI_AGENT_PARAMS"))

AUTH_USERS_FILE = "../../data/authorized_users.json"