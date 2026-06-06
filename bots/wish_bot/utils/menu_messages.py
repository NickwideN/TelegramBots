"""Активное меню в чате: отслеживание и скрытие устаревших кнопок."""

from __future__ import annotations

import logging

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.state import State
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.manager.message_manager import _combine

from bots.wish_bot.services import get_repository
from bots.wish_bot.states.menu import MenuSG

_NAV_BACK_STACK_KEY = "nav_back_stack"

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


def root_dialog_manager(dialog_manager: DialogManager) -> DialogManager:
    manager = dialog_manager
    while getattr(manager, "manager", None) is not None:
        manager = manager.manager
    return manager


async def send_main_menu_as_new_message(dialog_manager: DialogManager) -> None:
    """Отправить основное меню новым сообщением, не трогая клавиатуры выше."""
    manager = root_dialog_manager(dialog_manager)
    manager.dialog_data.pop(_NAV_BACK_STACK_KEY, None)
    manager.dialog_data.pop("nav_back_state", None)

    if manager.middleware_data.get("current_group"):
        await manager.switch_to(MenuSG.group)
    else:
        await manager.switch_to(MenuSG.no_group)

    bot = manager.middleware_data["bot"]
    new_message = await manager.dialog().render(manager)
    sent_message = await manager.message_manager.send_message(bot, new_message)
    manager._save_last_message(_combine(new_message, sent_message))
    manager.show_mode = ShowMode.NO_UPDATE


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
