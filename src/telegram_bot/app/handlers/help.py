from aiogram import types
from aiogram import Router

router = Router()
router.name = 'help'

@router.message(lambda message: message.text.startswith('/help'))
async def help_cmd(message: types.Message):
    """Обработчик команды /help"""
    help_text = (
        "📚 Справка по использованию бота:\n\n"
        "1. Отправьте любой запрос для поиска информации в вики\n"
        "2. Выберите интересующую тему из предложенных\n"
        "3. Нажмите на кнопку для получения подробной информации\n"
        "4. Оставьте обратную связь о качестве ответа\n\n"
        "Команды:\n"
        "/start - начать работу с ботом\n"
        "/status - проверить свой статус в системе\n"
        "/end - завершить текущий диалог"
    )
    await message.reply(help_text)