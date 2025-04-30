from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Command
from aiogram import Router

from src.telegram_bot.app.loader import UserStates

router = Router()
router.name = 'end'

@router.message(Command("end"))
async def end_dialog(message: Message, state: FSMContext):
    """Команда для выхода из состояния диалога"""
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Вы не находитесь в активном состоянии.")
        return

    await state.clear()
    await message.answer("Вы вышли из диалога. Если захотите начать заново, просто отправьте сообщение.")


@router.message(Command("reset"))
async def reset_cmd(message: Message, state: FSMContext):
    """Команда для сброса состояния пользователя"""
    await state.clear()
    await state.set_state(UserStates.dialog)
    await message.answer("Ваше состояние сброшено и установлено как 'диалог'. Теперь вы можете задавать вопросы.")
