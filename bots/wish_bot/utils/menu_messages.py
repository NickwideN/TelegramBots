"""Активное меню в чате: отслеживание и скрытие устаревших кнопок."""

from __future__ import annotations

import logging

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.state import State
from aiogram_dialog import DialogManager

from bots.wish_bot.services import get_repository
from bots.wish_bot.states.menu import MenuSG

logger = logging.getLogger(__name__)

# Корневые экраны меню (не подразделы вроде «Мои группы»).
MENU_ROOT_STATES: frozenset[State] = frozenset(
    {
        MenuSG.welcome,
        MenuSG.welcome_invite,
        MenuSG.welcome_invite_invalid,
        MenuSG.no_group,
        MenuSG.group,
    }
)


async def hide_inline_keyboard(bot: Bot, chat_id: int, message_id: int) -> None:
    try:
        await bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
        )
    except TelegramBadRequest as error:
        message = (error.message or "").lower()
        if "message is not modified" in message:
            return
        if "message can't be edited" in message:
            return
        if "message to edit not found" in message:
            return
        if "message_id_invalid" in message:
            return
        raise


async def track_menu_message(dialog_manager: DialogManager) -> None:
    if not dialog_manager.has_context():
        return

    state = dialog_manager.current_context().state
    if state not in MENU_ROOT_STATES:
        return

    stack = dialog_manager.current_stack()
    message_id = stack.last_message_id
    if not message_id:
        return

    chat = dialog_manager.middleware_data.get("event_chat")
    user = dialog_manager.middleware_data.get("user")
    bot = dialog_manager.middleware_data.get("bot")
    if chat is None or user is None or bot is None:
        return

    repo = get_repository()
    previous = repo.replace_active_menu_message(
        telegram_id=user.telegram_id,
        chat_id=chat.id,
        message_id=message_id,
    )
    if previous is None:
        return

    prev_chat_id, prev_message_id = previous
    if prev_chat_id == chat.id and prev_message_id == message_id:
        return

    await hide_inline_keyboard(bot, prev_chat_id, prev_message_id)
