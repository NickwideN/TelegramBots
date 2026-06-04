from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from fluentogram import TranslatorRunner

from bots.wish_bot.services import get_repository
from bots.wish_bot.utils.send import answer_with_retry

router = Router()


def _is_tester(user_id: int, tester_ids: frozenset[int]) -> bool:
    return user_id in tester_ids


def _delete_db_keyboard(i18n: TranslatorRunner) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.get("button-delete-db"),
                    callback_data="delete_db:confirm",
                ),
            ],
        ],
    )


@router.message(Command(commands=["delete_db"]))
async def cmd_delete_db(
    message: Message,
    i18n: TranslatorRunner,
    tester_ids: frozenset[int],
) -> None:
    user_id = message.from_user.id if message.from_user else 0
    if not _is_tester(user_id, tester_ids):
        return

    await answer_with_retry(
        message,
        i18n.get("message-delete-db-warning"),
        reply_markup=_delete_db_keyboard(i18n),
    )


@router.callback_query(F.data == "delete_db:confirm")
async def callback_delete_db_confirm(
    callback: CallbackQuery,
    i18n: TranslatorRunner,
    tester_ids: frozenset[int],
) -> None:
    user_id = callback.from_user.id
    if not _is_tester(user_id, tester_ids):
        await callback.answer()
        return

    repo = get_repository()
    repo.purge_user_data(user_id)

    await callback.answer()
    if callback.message:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.edit_text(i18n.get("message-delete-db-done"))
