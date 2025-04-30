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
async def init_models():
    Base.metadata.create_all(bind=engine)


logging.basicConfig(level=logging.INFO)


async def on_startup():
    load_authorized_users()
    if ADMIN_ID:
        logging.info(f"Admin ID loaded: {ADMIN_ID}")
    else:
        logging.warning("Admin ID not loaded!")

    logging.info("Бот запущен")
    for router in routers:
        dp.include_router(router)

async def on_shutdown():
    logging.info("Shutting down...")
    try:
        agent.vectorstore.close()
    except Exception as e:
        logging.error(f"Error closing vector store: {e}")
    
    await dp.storage.close()
    logging.info("Bye!")


async def main():
    await init_models()
    await on_startup()
    try:
        await dp.start_polling(bot)
    finally:
        await on_shutdown()


if __name__ == '__main__':
    asyncio.run(main())
