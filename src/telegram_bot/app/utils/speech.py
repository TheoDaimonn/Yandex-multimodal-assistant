import os
import aiohttp
import aiofiles
import mimetypes

from pathlib import Path
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

SPEECH_PROVIDER = os.environ["SPEECH_PROVIDER"].lower()

if SPEECH_PROVIDER == "yandex":
    SPEECH_URL = os.environ.get("SPEECH_URL", "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize")
    SPEECH_FOLDER_ID = os.environ["YANDEX_FOLDER_ID"]
    SPEECH_API_KEY = os.environ["YANDEX_API_KEY"]
elif SPEECH_PROVIDER == "openai":
    SPEECH_URL = os.environ["SPEECH_URL"]
    SPEECH_API_KEY = os.environ.get("SPEECH_API_KEY") or os.environ["API_KEY"]
    SPEECH_MODEL = os.environ.get("SPEECH_MODEL", "openai/whisper-large-v3")
    SPEECH_RESPONSE_FORMAT = os.environ.get("SPEECH_RESPONSE_FORMAT", "text")
    SPEECH_TEMPERATURE = os.environ.get("SPEECH_TEMPERATURE", "0.5")
    SPEECH_LANGUAGE = os.environ.get("SPEECH_LANGUAGE", "ru")
else:
    raise ValueError(f"Unsupported SPEECH_PROVIDER: {SPEECH_PROVIDER}")
    
async def transcribe_speechkit(audio_path: str) -> str:
    url = SPEECH_URL
    if SPEECH_PROVIDER == "openai":
        audio = Path(audio_path)
        async with aiohttp.ClientSession() as session:
            async with aiofiles.open(audio, 'rb') as f:
                file_content = await f.read()

            if not file_content:
                return ""

            data = aiohttp.FormData()
            data.add_field(
                "file",
                file_content,
                filename=audio.name,
                content_type=mimetypes.guess_type(audio.name)[0] or "application/octet-stream",
            )
            data.add_field("model", SPEECH_MODEL)
            data.add_field("response_format", SPEECH_RESPONSE_FORMAT)
            data.add_field("temperature", SPEECH_TEMPERATURE)
            data.add_field("language", SPEECH_LANGUAGE)

            headers = {"Authorization": f"Bearer {SPEECH_API_KEY}"}
            async with session.post(url, headers=headers, data=data) as resp:
                resp.raise_for_status()
                if SPEECH_RESPONSE_FORMAT == "text":
                    return (await resp.text()).strip()

                result = await resp.json()
                return result.get("text", "")
    
    elif SPEECH_PROVIDER == "yandex":
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
