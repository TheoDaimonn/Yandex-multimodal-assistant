import asyncio
import os
import aiohttp

from aiogram import F, Router
from aiogram.types import Message

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

SPEECH_FOLDER_ID = os.environ["FOLDER_ID"]
SPEECH_API_KEY    = os.environ["API_KEY"]

async def transcribe_ya_speechkit(audio_path: str) -> str:
    url = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"
    params = {
        "lang":     "ru-RU",
        "folderId": SPEECH_FOLDER_ID,
        # опционально: topic=general
    }
    headers = {
        "Authorization": f"Api-Key {SPEECH_API_KEY}",
        # "Content-Type": "application/octet-stream"  # aiohttp выставит сам
    }

    # читаем сырой поток
    async with aiohttp.ClientSession() as session:
        with open(audio_path, "rb") as f:
            data = f.read()
        if not data:
            return ""
        async with session.post(url, params=params, headers=headers, data=data) as resp:
            result = await resp.json()
            print("STT response:", result)
            return result.get("result", "")
