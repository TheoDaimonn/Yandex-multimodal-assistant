import asyncio
import logging
import json
from aiogram import F
from aiogram.types import Message
from aiogram import Router
from sqlalchemy import update
from src.telegram_bot.app.models.models import User
from src.telegram_bot.app.dao.user_dao import UserDAO


from src.telegram_bot.app.handlers.answer_to_user import answer_to_user_func
from src.telegram_bot.app.utils.profile_query import profile_query

router = Router()
router.name = 'start'

WELCOME = (
    "👋 *Привет!* Я бот приёмной комиссии **МАИ**.\n\n"
    "🔍 Помогу найти всё, что нужно для поступления — от проходных баллов до общежития.\n"
    "Задавай вопросы, а я быстро подберу ответы!\n\n"
    "📌 Доступные команды:\n"
    "• /start — 🚀 Старт\n"
    "• /instruction — 📑 Инструкция\n"
    "• /help — 🆘 Помощь специалиста\n\n"
    "Готов начать? Просто напиши свой вопрос хоть на китайском 🙂"
)

INSTRUCTION = (
    "📑 *Как пользоваться ботом*\n\n"
    "1️⃣  Сформулируйте вопрос обычным текстом — я отвечу мгновенно.\n"
    "2️⃣  Полезные команды:\n"
    "   • /start — перезапуск и главное меню\n"
    "   • /instruction — эта инструкция\n"
    "   • /help — связаться со специалистом\n\n"
    "💡 *Советы:*\n"
    "• Задавайте конкретные вопросы: _«какой проходной балл на 2024?»_\n"
    "• Можно задавать несколько вопросов одним сообщением\n"
    "• Если нужна живая помощь — используйте /help.\n"
)

HELP = (
    "🆘 *Помощь специалиста*\n\n"
    "Ваше сообщение отправлено сотруднику приёмной комиссии.\n"
    "Пожалуйста, опишите проблему подробнее — так мы быстрее поможем\n"
    "[Максим](https://t.me/hell_lumpen) обязательно поможет вам в любое время дня и ночи♥️"
)

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


@router.message(~F.text.startswith('/'))
async def handle_text(message: Message, dao: UserDAO):
    tg_id = message.from_user.id

    # Обновляем сессию пользователя

    user, need_summary = await dao.update_user_session(
        tg_id=tg_id,
        new_message=message.text,
        is_bot=False
    )

    # Если нужно - запускаем генерацию саммари в фоне
    if need_summary:
        await asyncio.create_task(
            generate_summary_background(dao, user, id=tg_id)
        )

    response = await answer_to_user_func('ass')

    await dao.update_user_session(
        tg_id=tg_id,
        new_message=response,
        is_bot=True  # Это сообщение от бота
    )
    # Ваша функция генерации ответа
    await message.answer(response)


async def generate_summary_background(dao: UserDAO, user: User, id):
    """Фоновая задача для генерации саммари"""
    try:
        print('зашли в портрет')
        res = await dao.return_chat_history(id)
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