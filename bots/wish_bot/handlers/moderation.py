from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
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
from bots.wish_bot.utils.send import answer_with_retry

router = Router()


def _require_admin(
    current_group: Group | None,
    user: User,
    i18n: TranslatorRunner,
) -> Group | None:
    if current_group is None:
        return None
    if current_group.admin_id != user.telegram_id:
        return None
    return current_group


def _member_label(user_id: int) -> str:
    repo = get_repository()
    member = repo.get_user(user_id)
    if not member:
        return str(user_id)
    name = member.first_name or "—"
    username_part = f" (@{member.username})" if member.username else ""
    return f"{name}{username_part}"


def _user_i18n(user_id: int, hub: TranslatorHub, fallback: TranslatorRunner) -> TranslatorRunner:
    repo = get_repository()
    user = repo.get_user(user_id)
    locale = user.locale if user and user.locale in ("ru", "en") else "ru"
    return hub.get_translator_by_locale(locale=locale)


async def _send_members_list(
    message: Message,
    i18n: TranslatorRunner,
    group: Group,
) -> None:
    repo = get_repository()
    member_ids = [
        uid for uid in repo.list_group_members(group.id)
        if uid != group.admin_id
    ]

    if not member_ids:
        await answer_with_retry(message, i18n.get("message-no-group-members"))
        return

    await answer_with_retry(message, i18n.get("message-group-members-header"))

    for user_id in member_ids:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=i18n.get("button-block"),
                        callback_data=f"block_member:{group.id}:{user_id}",
                    ),
                ],
            ],
        )
        await answer_with_retry(
            message,
            _member_label(user_id),
            reply_markup=keyboard,
        )


async def _send_blocked_list(
    message: Message,
    i18n: TranslatorRunner,
    group: Group,
) -> None:
    repo = get_repository()
    blocked_ids = repo.list_blocked_members(group.id)

    if not blocked_ids:
        await answer_with_retry(message, i18n.get("message-no-blocked-members"))
        return

    await answer_with_retry(message, i18n.get("message-group-blocked-header"))

    for user_id in blocked_ids:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=i18n.get("button-unblock"),
                        callback_data=f"unblock_member:{group.id}:{user_id}",
                    ),
                ],
            ],
        )
        await answer_with_retry(
            message,
            _member_label(user_id),
            reply_markup=keyboard,
        )


@router.message(Command(commands=["group_members"]))
async def cmd_group_members(
    message: Message,
    i18n: TranslatorRunner,
    user: User,
    current_group: Group | None,
) -> None:
    """Список участников группы (только админ)."""
    group = _require_admin(current_group, user, i18n)
    if current_group is None:
        await answer_with_retry(message, i18n.get("message-no-group"))
        return
    if group is None:
        await answer_with_retry(message, i18n.get("message-group-not-admin"))
        return

    await _send_members_list(message, i18n, group)


@router.message(Command(commands=["group_blocked"]))
async def cmd_group_blocked(
    message: Message,
    i18n: TranslatorRunner,
    user: User,
    current_group: Group | None,
) -> None:
    """Список заблокированных (только админ)."""
    group = _require_admin(current_group, user, i18n)
    if current_group is None:
        await answer_with_retry(message, i18n.get("message-no-group"))
        return
    if group is None:
        await answer_with_retry(message, i18n.get("message-group-not-admin"))
        return

    await _send_blocked_list(message, i18n, group)


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
