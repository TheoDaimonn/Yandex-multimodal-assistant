import asyncio
import os
import aiohttp

from aiogram import F, Router
from aiogram.types import Message

from src.telegram_bot.app.loader import bot
from src.telegram_bot.app.dao.user_dao import UserDAO
from src.telegram_bot.app.handlers.answer_to_user import answer_to_user_func
from src.telegram_bot.app.handlers.start import generate_summary_background

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

router = Router()
router.name = "voice"

@router.message(F.content_type == "voice")
async def voice_handler(message: Message, dao: UserDAO):
    print('z nffffffffffffffffffffffffffffffffff')
    # 1) скачиваем голос в файл
    file_info = await bot.get_file(message.voice.file_id)
    local_path = os.path.join(DOWNLOAD_DIR, f"{message.voice.file_id}.ogg")
    await bot.download_file(file_info.file_path, destination_file=local_path)

    # 2) транскрибируем
    text = await transcribe_ya_speechkit(local_path)

    # os.remove(local_path)

    if not text:
        return await message.reply("❌ не удалось распознать речь. Попробуйте ещё раз.")

    # 3) продолжаем как с текстом
    await message.answer(f"📝 вы сказали: «{text}»")

    user, need_summary = await dao.update_user_session(
        tg_id=message.from_user.id,
        new_message=text,
        is_bot=False
    )

    if need_summary:
        asyncio.create_task(
            generate_summary_background(dao, user, tg_id=message.from_user.id)
        )

    response = await answer_to_user_func({"text": text})
    await dao.update_user_session(
        tg_id=message.from_user.id,
        new_message=response,
        is_bot=True
    )
    await message.answer(response)
