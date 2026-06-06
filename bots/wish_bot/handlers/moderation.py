from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery
from fluentogram import TranslatorHub, TranslatorRunner

from bots.wish_bot.services import get_repository
from bots.wish_bot.services.repository import (
    CannotBlockAdminError,
    CannotBlockSelfError,
    Group,
    NotGroupAdminError,
    User,
    UserNotMemberError,
)

router = Router()


def _user_i18n(user_id: int, hub: TranslatorHub, fallback: TranslatorRunner) -> TranslatorRunner:
    repo = get_repository()
    user = repo.get_user(user_id)
    locale = user.locale if user and user.locale in ("ru", "en") else "ru"
    return hub.get_translator_by_locale(locale=locale)


@router.callback_query(F.data.startswith("block_member:"))
async def callback_block_member(
    callback: CallbackQuery,
    bot: Bot,
    i18n: TranslatorRunner,
    user: User,
    current_group: Group | None,
    **kwargs,
) -> None:
    parts = callback.data.split(":")
    group_id = int(parts[1])
    target_id = int(parts[2])

    if current_group is None or current_group.id != group_id:
        await callback.answer(i18n.get("message-no-group"), show_alert=True)
        return
    if current_group.admin_id != user.telegram_id:
        await callback.answer(i18n.get("message-group-not-admin"), show_alert=True)
        return

    repo = get_repository()
    try:
        repo.block_member(group_id, target_id, user.telegram_id)
    except CannotBlockSelfError:
        await callback.answer(i18n.get("message-cannot-block-self"), show_alert=True)
        return
    except CannotBlockAdminError:
        await callback.answer(i18n.get("message-cannot-block-admin"), show_alert=True)
        return
    except UserNotMemberError:
        await callback.answer(i18n.get("message-member-not-found"), show_alert=True)
        return
    except NotGroupAdminError:
        await callback.answer(i18n.get("message-group-not-admin"), show_alert=True)
        return

    hub: TranslatorHub | None = kwargs.get("_translator_hub")
    if hub:
        target_i18n = _user_i18n(target_id, hub, i18n)
        try:
            await bot.send_message(
                chat_id=target_id,
                text=target_i18n.get(
                    "message-user-blocked",
                    groupName=current_group.name,
                ),
            )
        except Exception:
            pass

    await callback.answer(i18n.get("message-member-blocked"))
    if callback.message:
        await callback.message.delete()


@router.callback_query(F.data.startswith("unblock_member:"))
async def callback_unblock_member(
    callback: CallbackQuery,
    i18n: TranslatorRunner,
    user: User,
    current_group: Group | None,
) -> None:
    parts = callback.data.split(":")
    group_id = int(parts[1])
    target_id = int(parts[2])

    if current_group is None or current_group.id != group_id:
        await callback.answer(i18n.get("message-no-group"), show_alert=True)
        return
    if current_group.admin_id != user.telegram_id:
        await callback.answer(i18n.get("message-group-not-admin"), show_alert=True)
        return

    repo = get_repository()
    try:
        repo.unblock_member(group_id, target_id, user.telegram_id)
    except NotGroupAdminError:
        await callback.answer(i18n.get("message-group-not-admin"), show_alert=True)
        return

    await callback.answer(i18n.get("message-member-unblocked"))
    if callback.message:
        await callback.message.delete()
