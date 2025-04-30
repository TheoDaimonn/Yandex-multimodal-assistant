from aiogram import BaseMiddleware
from typing import Callable, Awaitable, Any

from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from src.telegram_bot.app.dao.user_dao import UserDAO
from src.telegram_bot.app.database import AsyncSessionLocal

class DaoMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any]
    ) -> Any:
        async with AsyncSessionLocal() as session:
            data["dao"] = UserDAO(session)
            return await handler(event, data)