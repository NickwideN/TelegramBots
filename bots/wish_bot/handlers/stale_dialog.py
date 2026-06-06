"""Устаревшие callback-кнопки диалога и восстановление активного меню."""

from __future__ import annotations

import logging

from aiogram import Bot, Router
from aiogram.filters import ExceptionTypeFilter
from aiogram.types import CallbackQuery, ErrorEvent
from aiogram_dialog import DialogManager
from aiogram_dialog.api.exceptions import OutdatedIntent, UnknownIntent

from bots.wish_bot.handlers.commands import start_menu
from bots.wish_bot.services import get_repository
from bots.wish_bot.services.repository import Group, User
from bots.wish_bot.utils.menu_messages import hide_inline_keyboard, track_menu_message

logger = logging.getLogger(__name__)

router = Router()


def _is_active_menu_message(
    callback: CallbackQuery,
    user: User | None,
) -> bool:
    if callback.message is None or user is None:
        return False

    repo = get_repository()
    active = repo.get_active_menu_message(user.telegram_id)
    if active is None:
        return False

    chat_id, message_id = active
    return (
        callback.message.chat.id == chat_id
        and callback.message.message_id == message_id
    )


@router.errors(ExceptionTypeFilter(UnknownIntent, OutdatedIntent))
async def handle_stale_dialog_callback(
    event: ErrorEvent,
    bot: Bot,
    dialog_manager: DialogManager,
    user: User | None,
    current_group: Group | None,
) -> bool:
    callback = event.update.callback_query
    if callback is None:
        return True

    try:
        await callback.answer()
    except Exception:
        logger.debug("Could not answer stale callback", exc_info=True)

    if isinstance(event.exception, OutdatedIntent):
        if callback.message is not None:
            await hide_inline_keyboard(
                bot,
                callback.message.chat.id,
                callback.message.message_id,
            )
        return True

    if _is_active_menu_message(callback, user) and dialog_manager is not None:
        logger.info(
            "Recover active menu for user %s after lost dialog context",
            callback.from_user.id,
        )
        await start_menu(dialog_manager, current_group)
        await track_menu_message(dialog_manager)
        return True

    if callback.message is not None:
        await hide_inline_keyboard(
            bot,
            callback.message.chat.id,
            callback.message.message_id,
        )
    return True
