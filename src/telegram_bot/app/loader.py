from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from src.telegram_bot.app.config import config
from aiogram.client.default import DefaultBotProperties 
from aiogram.enums import ParseMode   
from src.telegram_bot.app.middleware import DaoMiddleware  # Добавьте этот импорт

bot = Bot(token=config.TG_API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()

# Регистрация middleware
dp.message.middleware(DaoMiddleware())
dp.callback_query.middleware(DaoMiddleware()) 