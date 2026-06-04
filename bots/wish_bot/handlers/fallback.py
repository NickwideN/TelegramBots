from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from fluentogram import TranslatorRunner

from bots.wish_bot.states.group import CreateGroupSG
from bots.wish_bot.utils.send import answer_with_retry

router = Router()


@router.message()
async def unknown_message(
    message: Message,
    i18n: TranslatorRunner,
    state: FSMContext,
) -> None:
    current = await state.get_state()
    if current == CreateGroupSG.waiting_name:
        await state.clear()

    await answer_with_retry(message, i18n.get("message-did-not-understand"))
