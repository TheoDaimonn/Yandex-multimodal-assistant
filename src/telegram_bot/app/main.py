import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from src.telegram_bot.app.config import config
from src.telegram_bot.app.utils.auth import load_authorized_users
from src.telegram_bot.app.handlers import routers
# from app.handlers.search import agent
from src.telegram_bot.app.loader import dp, bot, ADMIN_ID
from src.telegram_bot.app.database import Base, engine
from src.telegram_bot.app.models.models import User, Session
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from src.telegram_bot.app.config import config
from src.telegram_bot.app.utils.auth import load_authorized_users
from src.telegram_bot.app.handlers import routers
from src.telegram_bot.app.database import init_db

logging.basicConfig(level=logging.INFO)


async def on_startup():
    await init_db()  # Инициализируем БД при старте
    load_authorized_users()
    for router in routers:
        dp.include_router(router)
    logging.info("Бот запущен")


async def on_shutdown():
    logging.info("Shutting down...")
    await dp.storage.close()
    logging.info("Bye!")


async def main():
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    await on_startup()
    try:
        await dp.start_polling(bot)
    finally:
        await on_shutdown()


if __name__ == '__main__':
    asyncio.run(main())