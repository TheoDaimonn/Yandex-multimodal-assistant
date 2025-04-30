from aiogram import types
from aiogram import Router

router = Router()
router.name = 'help'

@router.message(lambda message: message.text.startswith('/help'))
async def help_cmd(message: types.Message):
    """Обработчик команды /help"""
    help_text = (
        "📚 Справка по использованию бота:\n\n"

    )
    await message.reply(help_text)