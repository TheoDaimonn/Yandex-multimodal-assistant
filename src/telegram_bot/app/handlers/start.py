import asyncio
import logging
from aiogram import F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram import Router
from datetime import datetime
import answer_to_user
import summarise

from src.telegram_bot.app.loader import bot, UserStates, authorized_users, pending_users
from src.telegram_bot.app.models.models import User
from src.telegram_bot.app.dao.user_dao import UserDAO

router = Router()
router.name = 'start'


@router.message(F.text, F.text.startswith('/start'))
async def start_cmd(message: Message, dao: UserDAO):
    welcome_text = (
        "👋бла бла бла приемка бла бла бла \n\n"
    )

    # Создаем/обновляем пользователя
    await dao.create_user(
        tg_id=message.from_user.id,
        username=message.from_user.username
    )

    await message.answer(welcome_text)


@router.message(F.text, ~F.text.startswith('/'))
async def handle_text(message: Message, state: FSMContext, dao: UserDAO):
    tg_id = message.from_user.id

    # Обновляем сессию пользователя
    user, need_summary = await dao.update_user_session(
        tg_id=tg_id,
        new_message=message.text
    )

    # Если нужно - запускаем генерацию саммари в фоне
    if need_summary:
        await asyncio.create_task(
            generate_summary_background(dao, user)
        )

    # Проверяем авторизацию
    current_state = await state.get_state()
    if current_state != UserStates.dialog:
        await state.set_state(UserStates.dialog)


    response = await answer_to_user  # Ваша функция генерации ответа
    await message.answer(response)


async def generate_summary_background(dao: UserDAO, user: User):
    """Фоновая задача для генерации саммари"""
    try:
        summary = await summarise(user.current_messages)  # Ваш агент
        await dao.session.execute(update(User).where(User.id == user.id).values(last_summary=summary)
        )
        await dao.session.commit()
    except Exception as e:
        logging.error(f"Ошибка генерации саммари: {e}")


async def generate_response(context: dict) -> str:
    """Генерация ответа с учетом контекста"""
    # Ваша логика формирования ответа
    if context.get('summary'):
        return "tropa tripi"  # Заглушка