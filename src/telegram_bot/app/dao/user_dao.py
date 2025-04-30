# src/telegram_bot/app/dao/user_dao.py
from datetime import datetime

from sqlalchemy.orm import Session
from src.telegram_bot.app.models.models import User

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.telegram_bot.app.models.models import User


class UserDAO:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_tg_id(self, tg_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.tg_id == tg_id))
        return result.scalars().first()

    async def create_user(self, tg_id: int, username: str = None) -> User:
        user = User(tg_id=tg_id, username=username, )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_user_to_admin(self, tg_id: int) -> User | None:
        user = await self.get_user_by_tg_id(tg_id)
        if user:
            user.is_admin = True
            await self.session.commit()
            await self.session.refresh(user)
        return user

    async def get_all_users(self) -> list[User]:
        result = await self.session.execute(select(User))
        return result.scalars().all()

    async def update_user_session(
            self,
            tg_id: int,
            new_message: str,
            is_bot: bool = False
    ) -> tuple[User, bool]:
        """Обновляет сессию пользователя и возвращает (user, need_summary)"""
        user = await self.get_user_by_tg_id(tg_id)
        need_summary = False

        if not user:
            user = await self.create_user(tg_id=tg_id)
            user.current_messages = [{"role": "user", "text": new_message}]
            user.message_count = 1
        else:
            messages = user.current_messages or []
            messages.append({
                "role": "assistant" if is_bot else "user",
                "text": new_message,
                "time": datetime.now().isoformat()
            })

            if not is_bot:
                user.message_count += 1
                need_summary = (user.message_count % 5 == 0 and len(messages) >= 3)

            user.current_messages = messages

        user.last_activity = datetime.now()
        await self.session.commit()
        return user, need_summary