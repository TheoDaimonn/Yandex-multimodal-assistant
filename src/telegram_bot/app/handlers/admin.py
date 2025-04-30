from aiogram import types
from src.telegram_bot.app.config import config
from src.telegram_bot.app.loader import dp, bot, UserStates
import logging
from aiogram import Router
from src.telegram_bot.app.loader import dp, bot, UserStates, authorized_users, ADMIN_ID
from src.telegram_bot.app.utils.auth import save_authorized_users


router = Router()
router.name = 'admin'

async def is_admin(user_id: int, username: str) -> bool:
    admin_username = config.ADMIN_USERNAME.lstrip('@')
    return username == admin_username or user_id == ADMIN_ID

@router.message(lambda message: message.text == '/admin')
async def admin_cmd(message: types.Message):
    """Команда для установки администратора"""
    if message.from_user.username == config.ADMIN_USERNAME.lstrip('@'):
        global ADMIN_ID
        ADMIN_ID = message.from_user.id
        authorized_users.add(ADMIN_ID)
        save_authorized_users()
        logging.info(f"Admin set: ID={ADMIN_ID}, username={message.from_user.username}")
        await message.reply("Вы установлены как администратор.")
    else:
        logging.warning(f"Admin command rejected for user {message.from_user.username}")
        await message.reply("У вас нет прав для выполнения этой команды.")

@router.message(lambda message: message.text == '/users')
async def users_cmd(message: types.Message):
    """Команда для просмотра авторизованных пользователей"""
    if not await is_admin(message.from_user.id, message.from_user.username):
        await message.reply("Эта команда доступна только администраторам.")
        return
    
    if not authorized_users:
        await message.reply("Нет авторизованных пользователей.")
        return
    
    users_text = "Авторизованные пользователи:\n\n"
    for i, user_id in enumerate(authorized_users, 1):
        users_text += f"{i}. ID: {user_id}\n"

    await message.reply(users_text)

@router.message(lambda message: message.text.startswith('/authorize'))
async def authorize_cmd(message: types.Message):
    """Команда для ручной авторизации пользователя по ID"""
    if not await is_admin(message.from_user.id, message.from_user.username):
        await message.reply("Эта команда доступна только администраторам.")
        return
    
    parts = message.text.split()
    if len(parts) != 2:
        await message.reply("Использование: /authorize <id_пользователя>")
        return
    
    try:
        user_id = int(parts[1])
        authorized_users.add(user_id)
        save_authorized_users()
        
        await message.reply(f"Пользователь с ID {user_id} успешно авторизован.")
        
        # Отправляем уведомление пользователю
        try:
            await bot.send_message(
                user_id,
                "Вы были авторизованы администратором. Теперь вы можете использовать бота."
            )
            await dp.current_state(user=user_id, chat=user_id).set_state(UserStates.dialog.state)
        except Exception as e:
            logging.error(f"Ошибка при отправке уведомления пользователю: {e}")
            await message.reply(f"Не удалось отправить уведомление пользователю: {e}")
    
    except ValueError:
        await message.reply("ID пользователя должен быть числом.")

@router.message(lambda message: message.text.startswith('/setadmin'))
async def setadmin_cmd(message: types.Message):
    """Команда для установки администратора по ID"""
    parts = message.text.split()
    if len(parts) != 2:
        await message.reply("Использование: /setadmin <id_пользователя>")
        return
    
    try:
        user_id = int(parts[1])
        global ADMIN_ID
        ADMIN_ID = user_id
        authorized_users.add(user_id)
        save_authorized_users()
        
        await message.reply(f"Пользователь с ID {user_id} установлен как администратор.")
        
        # Отправляем уведомление новому администратору
        try:
            await bot.send_message(
                user_id,
                "Вы были назначены администратором бота."
            )
        except Exception as e:
            logging.error(f"Ошибка при отправке уведомления новому администратору: {e}")
            await message.reply(f"Не удалось отправить уведомление новому администратору: {e}")
    
    except ValueError:
        await message.reply("ID пользователя должен быть числом.")
