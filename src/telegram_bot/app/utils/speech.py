import os
import aiohttp
import aiofiles

from pathlib import Path
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

SPEECH_URL = os.environ["SPEECH_URL"]
SPEECH_PROVIDER = os.environ["SPEECH_PROVIDER"]

if SPEECH_PROVIDER == "Yandex":
    SPEECH_URL = os.environ.get("SPEECH_URL", "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize")
    SPEECH_FOLDER_ID = os.environ["FOLDER_ID"]
    SPEECH_API_KEY = os.environ["API_KEY"]
    
async def transcribe_speechkit(audio_path: str) -> str:
    url = SPEECH_URL
    if SPEECH_PROVIDER == "Local":
        audio_path = Path(audio_path)
        async with aiohttp.ClientSession() as session:
            async with aiofiles.open(audio_path, 'rb') as f:
                file_content = await f.read()
            
            # Формирование данных для отправки
            data = aiohttp.FormData()
            data.add_field('file', 
                        file_content,
                        filename=audio_path.name,
                        content_type='audio/wav')
            
            if not data:
                return ""
            async with session.post(url, data=data) as resp:
                json_object = await resp.json()
                if not json_object:
                    return ""
                return json_object["text"]
    
    elif SPEECH_PROVIDER == "Yandex":
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
