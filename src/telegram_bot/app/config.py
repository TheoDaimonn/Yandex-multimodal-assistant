from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from typing import Optional, List
from FlagEmbedding import BGEM3FlagModel
import os
from oauth2client.service_account import ServiceAccountCredentials
from aiogram.utils.markdown import hlink
from dotenv import load_dotenv
import json

load_dotenv(override=True)

class Config(BaseSettings):
    TG_API_TOKEN: str
    ADMIN_USERNAME: str
    WIKI_AGENT_PARAMS: dict = {}
    
config = Config()

# ADMIN_ID = None
print(config.ADMIN_USERNAME)

WIKI_AGENT_PARAMS = json.loads(os.getenv("WIKI_AGENT_PARAMS"))

AUTH_USERS_FILE = "data/authorized_users.json"