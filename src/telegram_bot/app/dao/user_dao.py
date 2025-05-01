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

    async def get_all_users(self) -> list[User]:
        result = await self.session.execute(select(User))
        return list(result.scalars().all())

    async def return_chat_history(self, tg_id) -> str:
        result = await self.session.execute(select(User.current_messages).where(User.tg_id == tg_id))
        result = result.scalars().first()
        return "".join(str(result))

    async def return_all_chat_history(self) -> str:
        result = await self.session.execute(select(User.current_messages))
        messages = result.scalars().all()
        return "\n".join(str(msg) if msg else "" for msg in messages)

    async def return_all_summary(self) -> str:
        result = await self.session.execute(select(User.last_summary))
        messages = result.scalars().all()
        return "\n".join(str(msg) if msg else "" for msg in messages)

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
            user.current_messages = [{"role": "assistant" if is_bot else "user", "text": new_message}]
            user.message_count = 1

        else:

            user.current_messages.append({
                "role": "assistant" if is_bot else "user",
                "text": new_message,
            })

            if not is_bot:
                user.message_count += 1
                need_summary = (user.message_count % 5 == 0 and user.message_count >= 3)


        user.last_activity = datetime.now()
        await self.session.commit()
        return user, need_summary
    
    async def get_last_n_messages(self, tg_id: int, n: int = 3) -> list[dict]:
        result = await self.session.execute(
            select(User.current_messages).where(User.tg_id == tg_id)
        )
        messages = result.scalars().first() or []
        return messages[-n*2:]

