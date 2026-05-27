from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from fluentogram import TranslatorHub

from bots.wish_bot.services import get_repository


class TranslatorRunnerMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        tg_user: User | None = data.get("event_from_user")
        hub: TranslatorHub | None = data.get("_translator_hub")

        if hub is None:
            return await handler(event, data)

        locale = "ru"
        if tg_user:
            repo = get_repository()
            db_user = repo.get_user(tg_user.id)
            if db_user and db_user.locale in ("ru", "en"):
                locale = db_user.locale
            elif tg_user.language_code in ("ru", "en"):
                locale = tg_user.language_code

        data["i18n"] = hub.get_translator_by_locale(locale=locale)
        return await handler(event, data)
