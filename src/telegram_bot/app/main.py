from src.telegram_bot.app.loader import dp, bot
import asyncio
import logging
from aiogram.types import BotCommand
from aiogram import Bot, Dispatcher
from src.telegram_bot.app.config import config
from src.telegram_bot.app.handlers import routers
from src.telegram_bot.app.database import init_db

logging.basicConfig(level=logging.INFO)

async def on_startup():
    await init_db()  # Инициализируем БД при старте
    for router in routers:
        dp.include_router(router)
    logging.info("Бот запущен")

    await bot.set_my_commands([
        BotCommand(command="start", description="🚀 Старт"),
        BotCommand(command="instruction", description="📑 Инструкция"),
        BotCommand(command="help", description="🆘 Помощь специалиста"),
    ])

async def on_shutdown():
    logging.info("Shutting down...")
    await dp.storage.close()
    logging.info("Bye!")


async def main():

    await on_startup()
    try:
        await dp.start_polling(bot)
    finally:
        await on_shutdown()


if __name__ == '__main__':
    asyncio.run(main())