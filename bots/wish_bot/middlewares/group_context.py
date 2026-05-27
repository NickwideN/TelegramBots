from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User as TgUser

from bots.wish_bot.services import get_repository
from bots.wish_bot.services.repository import Group, User


class GroupContextMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        tg_user: TgUser | None = data.get("event_from_user")
        if tg_user is None:
            return await handler(event, data)

        repo = get_repository()
        user = repo.upsert_user(
            telegram_id=tg_user.id,
            username=tg_user.username,
            first_name=tg_user.first_name,
        )
        data["user"] = user

        current_group: Group | None = None
        if user.current_group_id is not None:
            current_group = repo.get_group(user.current_group_id)
        data["current_group"] = current_group

        return await handler(event, data)
