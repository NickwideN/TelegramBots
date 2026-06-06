from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message
from fluentogram import TranslatorRunner

from bots.wish_bot.states.group import CreateGroupSG
from bots.wish_bot.states.wish import AddWishSG, CompleteWishSG
from bots.wish_bot.utils.send import answer_with_retry

router = Router()


@router.message(StateFilter(default_state))
async def unknown_message(
    message: Message,
    i18n: TranslatorRunner,
    state: FSMContext,
) -> None:
    current = await state.get_state()
    if current == CreateGroupSG.waiting_name:
        await state.clear()

    await answer_with_retry(message, i18n.get("message-did-not-understand"))


@router.message(StateFilter(AddWishSG.waiting_text, CompleteWishSG.waiting_message))
async def unknown_message_in_wish_flow(
    message: Message,
    i18n: TranslatorRunner,
) -> None:
    await answer_with_retry(message, i18n.get("message-did-not-understand"))
