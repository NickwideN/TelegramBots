from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from bots.wish_bot.utils.menu_messages import track_menu_message


class MenuMessageMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        result = await handler(event, data)
        dialog_manager = data.get("dialog_manager")
        if dialog_manager is not None:
            await track_menu_message(dialog_manager)
        return result
