
import asyncio
import logging
import json
from json import JSONDecodeError

from aiogram import F
from aiogram.types import Message, ContentType
from aiogram import Router
from sqlalchemy import update
from aiogram.types import (
    Message, ContentType, InlineKeyboardButton,
    InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery, BotCommand
)
from aiogram.types import (
    Message, ContentType, InlineKeyboardButton,
    InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery, BotCommand
)
from src.telegram_bot.app.models.models import User
from src.telegram_bot.app.dao.user_dao import UserDAO

from src.telegram_bot.app.handlers.answer_to_user import answer_to_user_func
from src.telegram_bot.app.utils.messages import answer_long_message
from src.telegram_bot.app.utils.profile_query import profile_query
from src.telegram_bot.app.utils.speech import transcribe_speechkit

import asyncio
import os
import aiohttp

from src.telegram_bot.app.loader import bot

router = Router()
router.name = 'start'

DOWNLOAD_DIR = "downloads"

FAQ_QUESTIONS = [
    "Какие проходные баллы в 2024?",
    "Сроки подачи документов?",
    "Какие нужны документы?",
    "Сколько стоит обучение?",
    "Условия в общежитии?"
]

WELCOME = (
    "👋 *Привет!* Я бот приёмной комиссии **МАИ**.\n\n"
    "🔍 Помогу найти всё, что нужно для поступления — от проходных баллов до общежития.\n"
    "Жду твои вопросики! \n\n"
    "📌 Доступные команды:\n"
    "• /start — 🚀 Старт\n"
    "• /instruction — 📑 Инструкция\n"
    "• /help — 🆘 Помощь специалиста\n"
    "• /questions — ❓ Частые вопросы\n\n"
    "Готов начать? Просто напиши свой вопрос, хоть на китайском 🙂"
)

INSTRUCTION = (
    "📑 *Как пользоваться ботом*\n\n"
    "1️⃣  Сформулируйте запрос — я отвечу мгновенно (а можно даже записать голосовое 😎)\n"
    "2️⃣  Полезные команды:\n"
    "   • /start — перезапуск и главное меню\n"
    "   • /instruction — эта инструкция\n"
    "   • /help — связаться со специалистом\n"
    "   • /questions — частые вопросы\n\n"
    "💡 *Советы:*\n"
    "• Задавайте конкретные вопросы: _«какой проходной балл на 2024?»_\n"
    "• Можно задавать несколько в одном сообщении\n"
    "• Если нужна живая помощь — используйте /help\n"
)

HELP = (
    "🆘 *Помощь специалиста*\n\n"
    "Ваше сообщение отправлено сотруднику приёмной комиссии.\n"
    "Пожалуйста, опишите проблему подробнее — так мы быстрее поможем\n"
    "[Максим](https://t.me/hell_lumpen) обязательно поможет вам в любое время дня и ночи♥️"
)

async def get_last_n_messages(self, tg_id: int, n: int = 3) -> list[dict]:
    result = await self.session.execute(select(User.current_messages).where(User.tg_id == tg_id))
    messages = result.scalars().first() or []
    return messages[-n*2:]  # последние n пар (пользователь+бот)

        
@router.message(F.text.startswith('/start'))
async def start_cmd(message: Message, dao: UserDAO):

    user = await dao.get_user_by_tg_id(message.from_user.id)
    if not user:
        user = await dao.create_user(
            tg_id=message.from_user.id,
            username=message.from_user.username
        )
        logging.info(f"Создан новый пользователь: {user.tg_id}")
    else:
        logging.info(f"Пользователь уже существует: {user.tg_id}")

    await message.answer(WELCOME)

@router.message(F.text.startswith('/getdata'))
async def start_cmd(message: Message, dao: UserDAO):

    print(await dao.return_all_summary())
    print(await dao.return_all_chat_history())

@router.message(F.text.startswith('/get_summary'))
async def start_cmd(message: Message, dao: UserDAO):
    tg_id = message.from_user.id
    responce = await dao.return_users_summary(tg_id)
    data = {}
    try:
        data = json.loads(responce)  # -> получаем словарь {"raw": "..."}
        inner_json_str = data["raw"].replace("```json", "").replace("```", "").strip()

        # Затем парсим внутренний JSON
        inner_data = json.loads(inner_json_str)
        summary_notes = inner_data["summary_notes"]
    except JSONDecodeError:
        await message.answer("О Вас пока что недостаточно информации( ")
        return

    await answer_long_message(message, summary_notes)

@router.message(F.content_type == ContentType.TEXT, ~F.text.startswith("/"))
async def text_handler(message: Message, dao: UserDAO):

    tg_id = message.from_user.id
    user, need_summary = await dao.update_user_session(
        tg_id=tg_id,
        new_message=message.text,
        is_bot=False
    )
    history = await dao.get_last_n_messages(tg_id, n=3)
    for i in history:
        i["content"] = i.pop("text")
    context_messages = history + [{"role": "user", "content": message.text}]

    response = await answer_to_user_func(context_messages)

    if need_summary:
        await asyncio.create_task(
            generate_summary_background(dao, user, tg_id=tg_id)
        )

    await dao.update_user_session(
        tg_id=tg_id,
        new_message=response,
        is_bot=True  
    )


    await answer_long_message(message, response)

@router.message(F.content_type == ContentType.VOICE)
async def voice_handler(message: Message, dao: UserDAO):
    print('voice_handler')
    tg_id = message.from_user.id
    file = await bot.get_file(message.voice.file_id)
    file_path = file.file_path


    raw_io = await bot.download_file(file_path)   
    local_path = os.path.join(DOWNLOAD_DIR, f"{message.voice.file_id}.ogg")
    with open(local_path, "wb") as f:
        f.write(raw_io.read())     
    
    text = await transcribe_speechkit(local_path)
    print(text)

    try: os.remove(local_path)
    except: pass
    
    if not text:
        return await message.reply("❌ не удалось распознать речь.")
    
    await answer_long_message(message, f"📝 вы сказали: «{text}»")
    user, need = await dao.update_user_session(
        tg_id=tg_id, new_message=text, is_bot=False
    )
    if need:
        asyncio.create_task(generate_summary_background(dao, user, tg_id=tg_id))
    resp = await answer_to_user_func([{"role": "user", "content": text}])
    await dao.update_user_session(
        tg_id=tg_id, new_message=resp, is_bot=True
    )
    await answer_long_message(message, resp)

async def generate_summary_background(dao: UserDAO, user: User, tg_id: int):
    try:
        print('зашли в портрет')
 
        res = await dao.return_chat_history(tg_id)
        # print(res)
        summary = await profile_query(res) 
        print(summary)  
        await dao.session.execute(update(User).where(User.id == user.id).values(last_summary=summary))
        await dao.session.commit()
    except Exception as e:
        logging.error(f"Ошибка генерации саммари: {e}")

@router.message(F.text.startswith("/instruction"))
async def instruction_cmd(message: Message):
    await message.answer(INSTRUCTION)

@router.message(F.text.startswith("/help"))
async def help_cmd(message: Message):
    await message.answer(HELP)

def build_faq_inline():
    rows = [
        [InlineKeyboardButton(text=q, callback_data=f"faq:{q}")]
        for q in FAQ_QUESTIONS
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)

@router.message(F.text.startswith("/questions"))
@router.message(F.text == "❓ Частые вопросы")
async def faq_cmd(message: Message):
    await message.answer(
        "❓ Вот список частых вопросов, можете выбрать любой:\n"
        "Ты можешь выбрать себе любого питомца, которого ты захочешь 🦎",
        reply_markup=build_faq_inline()
    )

@router.callback_query(F.data.startswith("faq:"))
async def faq_callback(cq: CallbackQuery, dao: UserDAO):
    question = cq.data.split("faq:", 1)[1]
    await cq.answer()

    await dao.update_user_session(tg_id=cq.from_user.id, new_message=question, is_bot=False)
    response = await answer_to_user_func([{"role": "user", "content": question}])

    await dao.update_user_session(tg_id=cq.from_user.id, new_message=response, is_bot=True)

    await cq.message.edit_reply_markup()
    await answer_long_message(
        cq.message,
        f"❓ *Вопрос:* {question}\n\n💬 *Ответ:* {response}",
    )
