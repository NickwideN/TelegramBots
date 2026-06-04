"""Утилиты для отправки сообщений с учётом лимитов Telegram API."""
import asyncio
from typing import Any

from aiogram.exceptions import TelegramRetryAfter
from aiogram.types import Message


async def answer_with_retry(message: Message, text: str, **kwargs: Any) -> Message:
    """Отправка сообщения с повторной попыткой при 429."""
    max_retries = 3
    last_error: TelegramRetryAfter | None = None

    for attempt in range(max_retries + 1):
        try:
            return await message.answer(text, **kwargs)
        except TelegramRetryAfter as e:
            last_error = e
            if attempt < max_retries:
                await asyncio.sleep(max(1, e.retry_after))
            else:
                raise last_error

    raise last_error  # type: ignore[misc]
