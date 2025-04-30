import asyncio
from typing import List, Dict, Any

async def summarise(messages: List[Dict[str, Any]]) -> str:
    """
    Моковая функция генерации саммари
    Имитирует долгую обработку (1 минуту)
    На вход принимает список сообщений, но не использует их
    """
    print("⏳ Начато создание саммари (задержка 1 минута)...")
    await asyncio.sleep(60)  # Имитируем долгую обработку
    print("✅ Саммари готово!")
    return "Саммари по сессии: [тестовый результат]"