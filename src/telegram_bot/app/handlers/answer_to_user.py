import asyncio
from typing import List, Dict, Any

async def answer_to_user_func(context: Dict[str, Any]) -> str:
    """
    Моковая функция генерации ответа пользователю
    Имитирует долгую обработку (30 секунд)
    На вход принимает контекст, но не использует его
    """
    print("⏳ Формирую ответ пользователю (задержка 30 секунд)...")
    # await asyncio.sleep(5)  # Имитируем долгую обработку
    print("✅ Ответ готов!")
    return "Ответ для пользака: [тестовый ответ]"