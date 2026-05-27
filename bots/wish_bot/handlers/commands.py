from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from fluentogram import TranslatorRunner

from bots.wish_bot.services import get_repository
from bots.wish_bot.utils.send import answer_with_retry

router = Router()


def _language_keyboard(i18n: TranslatorRunner) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.get("button-language-russian"),
                    callback_data="lang:ru",
                ),
                InlineKeyboardButton(
                    text=i18n.get("button-language-english"),
                    callback_data="lang:en",
                ),
            ],
        ],
    )


async def _join_group_by_code(
    message: Message,
    invite_code: str,
    i18n: TranslatorRunner,
    user_id: int,
) -> bool:
    repo = get_repository()
    group = repo.get_group_by_invite(invite_code)
    if not group:
        await answer_with_retry(message, i18n.get("message-group-not-found"))
        return False

    if repo.is_blocked(group.id, user_id):
        await answer_with_retry(
            message,
            i18n.get("message-blocked-in-group", name=group.name),
        )
        return False

    if not repo.is_member(group.id, user_id):
        repo.add_member(group.id, user_id)
    repo.set_current_group(user_id, group.id)
    await answer_with_retry(message, i18n.get("help-text"))
    await answer_with_retry(message, i18n.get("message-joined-group", name=group.name))
    return True


@router.message(CommandStart())
async def cmd_start(
    message: Message,
    command: CommandObject,
    i18n: TranslatorRunner,
) -> None:
    """Обработчик команды /start."""
    user_id = message.from_user.id if message.from_user else 0
    args = (command.args or "").strip()

    if args.startswith("join_"):
        invite_code = args[5:]
        if invite_code:
            await _join_group_by_code(message, invite_code, i18n, user_id)
            return

    await answer_with_retry(message, i18n.get("help-text"))


@router.message(Command(commands=["help"]))
async def cmd_help(message: Message, i18n: TranslatorRunner) -> None:
    """Обработчик команды /help."""
    await answer_with_retry(message, i18n.get("help-text"))


@router.message(Command(commands=["language"]))
async def cmd_language(message: Message, i18n: TranslatorRunner) -> None:
    """Обработчик команды /language."""
    await answer_with_retry(
        message,
        i18n.get("message-choose-language"),
        reply_markup=_language_keyboard(i18n),
    )


@router.callback_query(F.data.startswith("lang:"))
async def callback_language(
    callback: CallbackQuery,
    i18n: TranslatorRunner,
    **kwargs,
) -> None:
    locale = callback.data.split(":")[1]
    if locale not in ("ru", "en"):
        await callback.answer()
        return

    user_id = callback.from_user.id
    repo = get_repository()
    repo.set_user_locale(user_id, locale)

    hub = kwargs.get("_translator_hub")
    if hub:
        i18n = hub.get_translator_by_locale(locale=locale)
    await callback.answer(i18n.get("message-language-selected"))
    if callback.message:
        await callback.message.edit_reply_markup(reply_markup=None)
