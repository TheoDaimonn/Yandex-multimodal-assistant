import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram import Router

from src.telegram_bot.app.loader import dp, bot, UserStates, authorized_users, pending_users, ADMIN_ID
from src.telegram_bot.app.utils.auth import save_authorized_users
from src.telegram_bot.app.handlers.admin import is_admin
from src.telegram_bot.app.config import config
from src.telegram_bot.app.utils.keyboards import create_inline_keyboard
# from app.handlers.search import handle_search

router = Router()
router.name = 'start'

@router.message(F.text, F.text.startswith('/start'))
async def start_cmd(message: Message):
    welcome_text = (
        "👋 Добро пожаловать в Wiki Поиск!\n\n"
        "Этот бот поможет вам быстро найти нужную информацию в корпоративном портале Wiki.\n\n"
        "Для начала работы напишите любое сообщение. Администратору придет уведомление "
        "о вашей регистрации, и после авторизации вы сможете отправлять запросы и получать результаты.\n\n"
        "Если у вас возникнут вопросы, используйте команду /help."
    )
    await message.answer(welcome_text)


@router.message(F.text, ~F.text.startswith('/'))
async def handle_text(message: Message, state: FSMContext):
    global ADMIN_ID
    user_id = message.from_user.id
    username = message.from_user.username

    if user_id not in authorized_users:
        if user_id in pending_users:
            await message.answer("Ожидайте подтверждения от администратора.")
            return

        # Проверка на админа
        if username == config.ADMIN_USERNAME.lstrip('@'):
            ADMIN_ID = user_id
            authorized_users.add(user_id)
            save_authorized_users()
            await state.set_state(UserStates.dialog)
            await message.answer("Вы вошли как администратор. Можете задать вопрос.")
            return

        pending_users[user_id] = username
        await state.set_state(UserStates.waiting_for_approval)
        await message.answer("Ваш запрос на регистрацию отправлен. Ожидайте подтверждения от администратора.")
        if ADMIN_ID:
            await bot.send_message(
                ADMIN_ID,
                f"Новая заявка от @{username} (ID: {user_id})\n"
                f"Первое сообщение: {message.text}",
                reply_markup=create_inline_keyboard(user_id)
            )
        else:
            admin_username = config.ADMIN_USERNAME.lstrip('@')
            logging.warning(f"ADMIN_ID not set, trying to find admin by username: {admin_username}")
            for admin_candidate_id in authorized_users:
                try:
                    admin_info = await bot.get_chat_member(admin_candidate_id, admin_candidate_id)
                    if admin_info.user.username == admin_username:
                        logging.info(f"Found admin by username: {admin_candidate_id}")
                        await bot.send_message(
                            admin_candidate_id,
                            f"Новая заявка от @{username} (ID: {user_id})\n"
                            f"Первое сообщение: {message.text}",
                            reply_markup=create_inline_keyboard(user_id)
                        )
                        break
                except Exception as e:
                    logging.error(f"Error checking admin candidate: {e}")
        return

    # Авторизован — обрабатываем запрос
    current_state = await state.get_state()
    if current_state != UserStates.dialog:
        await state.set_state(UserStates.dialog)

    await message.answer("tropa tripi")


@router.message(F.text, F.text.startswith('/status'))
async def status_cmd(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username

    status = []
    if await is_admin(user_id, username):
        status.append("Администратор")
    if user_id in authorized_users:
        status.append("Авторизованный пользователь")
    if user_id in pending_users:
        status.append("Ожидает подтверждения")

    if status:
        await message.answer(f"Ваш статус: {', '.join(status)}")
    else:
        await message.answer("У вас нет активного статуса")

