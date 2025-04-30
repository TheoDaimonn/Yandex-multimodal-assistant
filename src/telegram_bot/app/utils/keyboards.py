from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List


def create_search_keyboard(docs: List) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Ничего не подходит", callback_data="nothing_suitable")]
    ])
    return keyboard


def create_feedback_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👍 Дать обратную связь", callback_data="feedback_provide"),
            InlineKeyboardButton(text="⏭ Пропустить отзыв", callback_data="feedback_skip")
        ]
    ])
    return keyboard


def create_inline_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Создание инлайн-клавиатуры для администратора"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton(text="❌ Отказать", callback_data=f"deny_{user_id}")
        ]
    ])
    return keyboard
