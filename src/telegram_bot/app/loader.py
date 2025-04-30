from aiogram import Bot, Dispatcher
from src.telegram_bot.app.config import config
from src.telegram_bot.app.middleware import DaoMiddleware  # Добавьте этот импорт

bot = Bot(token=config.TG_API_TOKEN)
dp = Dispatcher()

# Регистрация middleware
dp.message.middleware(DaoMiddleware())
