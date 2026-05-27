from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from fluentogram import TranslatorRunner

from bots.wish_bot.services import get_repository
from bots.wish_bot.services.repository import Group, User, UserNotMemberError
from bots.wish_bot.utils.send import answer_with_retry

router = Router()


@router.message(Command(commands=["subscribe"]))
async def cmd_subscribe(
    message: Message,
    i18n: TranslatorRunner,
    user: User,
    current_group: Group | None,
) -> None:
    """Подписка на новые желания в текущей группе."""
    if current_group is None:
        await answer_with_retry(message, i18n.get("message-no-group"))
        return

    repo = get_repository()
    if repo.is_subscribed_wishes(current_group.id, user.telegram_id):
        await answer_with_retry(message, i18n.get("message-already-subscribed"))
        return

    try:
        repo.subscribe_wishes(current_group.id, user.telegram_id)
    except UserNotMemberError:
        await answer_with_retry(message, i18n.get("message-no-group"))
        return

    await answer_with_retry(
        message,
        i18n.get("message-subscribed", name=current_group.name),
    )


@router.message(Command(commands=["unsubscribe"]))
async def cmd_unsubscribe(
    message: Message,
    i18n: TranslatorRunner,
    user: User,
    current_group: Group | None,
) -> None:
    """Отписка от новых желаний в текущей группе."""
    if current_group is None:
        await answer_with_retry(message, i18n.get("message-no-group"))
        return

    repo = get_repository()
    if not repo.is_subscribed_wishes(current_group.id, user.telegram_id):
        await answer_with_retry(message, i18n.get("message-not-subscribed"))
        return

    repo.unsubscribe_wishes(current_group.id, user.telegram_id)
    await answer_with_retry(
        message,
        i18n.get("message-unsubscribed", name=current_group.name),
    )
