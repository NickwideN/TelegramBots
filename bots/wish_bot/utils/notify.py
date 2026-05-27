import asyncio
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from fluentogram import TranslatorHub

from bots.wish_bot.services import get_repository
from bots.wish_bot.services.repository import Group, Wish

logger = logging.getLogger(__name__)

NOTIFY_DELAY_SEC = 0.05
MAX_RETRIES = 3


def _subscriber_i18n(subscriber_id: int, hub: TranslatorHub):
    repo = get_repository()
    user = repo.get_user(subscriber_id)
    locale = user.locale if user and user.locale in ("ru", "en") else "ru"
    return hub.get_translator_by_locale(locale=locale)


async def _send_with_retry(
    bot: Bot,
    chat_id: int,
    text: str,
    reply_markup: InlineKeyboardMarkup,
) -> bool:
    for attempt in range(MAX_RETRIES + 1):
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=reply_markup,
            )
            return True
        except TelegramRetryAfter as e:
            if attempt < MAX_RETRIES:
                await asyncio.sleep(max(1, e.retry_after))
            else:
                logger.warning("Rate limit notifying user %s", chat_id)
                return False
        except Exception as e:
            logger.warning("Failed to notify user %s: %s", chat_id, e)
            return False
    return False


async def notify_new_wish(
    bot: Bot,
    group: Group,
    wish: Wish,
    author_id: int,
    hub: TranslatorHub,
) -> None:
    """Рассылка подписчикам о новом желании (кроме автора)."""
    repo = get_repository()
    subscribers = repo.list_wish_subscribers(group.id)
    recipients = [uid for uid in subscribers if uid != author_id]

    for index, subscriber_id in enumerate(recipients):
        i18n = _subscriber_i18n(subscriber_id, hub)
        text = i18n.get(
            "message-new-wish-notification",
            groupName=group.name,
            wishText=wish.text,
        )
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=i18n.get("button-take"),
                        callback_data=f"take:{wish.id}",
                    ),
                ],
            ],
        )
        await _send_with_retry(bot, subscriber_id, text, keyboard)
        if index < len(recipients) - 1:
            await asyncio.sleep(NOTIFY_DELAY_SEC)
