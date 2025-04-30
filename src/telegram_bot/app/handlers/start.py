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


@router.message(F.text.startswith('/start'))
async def start_cmd(message: Message, dao: UserDAO):
    welcome_text = (
        "👋бла бла бла приемка бла бла бла \n\n"
    )

    user = await dao.get_user_by_tg_id(message.from_user.id)
    if not user:
        user = await dao.create_user(
            tg_id=message.from_user.id,
            username=message.from_user.username
        )
        logging.info(f"Создан новый пользователь: {user.tg_id}")
    else:
        logging.info(f"Пользователь уже существует: {user.tg_id}")

    await message.answer(welcome_text)


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
            generate_summary_background(dao, user)
        )

    res = await dao.return_chat_history(tg_id)
    response = await answer_to_user_func(res)

    await dao.update_user_session(
        tg_id=tg_id,
        new_message=response,
        is_bot=True  # Это сообщение от бота
    )
    # Ваша функция генерации ответа
    await message.answer(response)


async def generate_summary_background(dao: UserDAO, user: User):
    """Фоновая задача для генерации саммари"""
    try:
        # tg_id = message.from_user.id
        
        print('зашли в портрет')
        res = await dao.return_chat_history(tg_id)
        summary = profile_query("я хочу поступить в 8 институт") 
        print(summary)  
        await dao.session.execute(update(User).where(User.id == user.id).values(last_summary=summary))
        await dao.session.commit()
    except Exception as e:
        logging.error(f"Ошибка генерации саммари: {e}")


async def generate_response(context: dict) -> str:
    """Генерация ответа с учетом контекста"""
    # Ваша логика формирования ответа
    if context.get('summary'):
        return "tropa tripi"  # Заглушка