import os
from typing import Protocol


class AnswerableMessage(Protocol):
    async def answer(self, text: str): ...


TELEGRAM_MESSAGE_LIMIT = int(os.getenv("TELEGRAM_MESSAGE_LIMIT", "4000"))


def split_message(text: str, limit: int = TELEGRAM_MESSAGE_LIMIT) -> list[str]:
    """Split text without exceeding Telegram's per-message character limit."""
    if limit <= 0:
        raise ValueError("Message limit must be positive")

    text = text.strip()
    chunks: list[str] = []

    while len(text) > limit:
        split_at = text.rfind("\n\n", 0, limit + 1)
        if split_at <= 0:
            split_at = text.rfind("\n", 0, limit + 1)
        if split_at <= 0:
            split_at = text.rfind(" ", 0, limit + 1)
        if split_at <= 0:
            split_at = limit

        chunks.append(text[:split_at].rstrip())
        text = text[split_at:].lstrip()

    if text:
        chunks.append(text)

    return chunks


async def answer_long_message(message: AnswerableMessage, text: str) -> None:
    for chunk in split_message(text):
        await message.answer(chunk)
