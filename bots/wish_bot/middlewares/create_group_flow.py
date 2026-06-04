from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, TelegramObject

from bots.wish_bot.states.group import CreateGroupSG


async def remove_inline_keyboard(bot: Bot, chat_id: int | None, message_id: int | None) -> None:
    if chat_id is None or message_id is None:
        return
    try:
        await bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=None,
        )
    except Exception:
        pass


async def cancel_group_visibility_choice(state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    await remove_inline_keyboard(
        bot,
        data.get("visibility_chat_id"),
        data.get("visibility_message_id"),
    )
    await state.clear()


class CreateGroupVisibilityMiddleware(BaseMiddleware):
    """Сбрасывает выбор видимости группы при любом сообщении пользователя."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, Message):
            state: FSMContext | None = data.get("state")
            if state and await state.get_state() == CreateGroupSG.waiting_visibility:
                bot: Bot | None = data.get("bot")
                if bot:
                    await cancel_group_visibility_choice(state, bot)
        return await handler(event, data)
