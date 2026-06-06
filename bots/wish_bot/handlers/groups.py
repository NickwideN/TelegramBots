from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram_dialog import DialogManager, StartMode
from fluentogram import TranslatorRunner

from bots.wish_bot.services import get_repository
from bots.wish_bot.services.repository import Group, RepositoryError, User
from bots.wish_bot.states.menu import MenuSG
from bots.wish_bot.utils.bot_info import make_invite_link

router = Router()


def _visibility_text(i18n: TranslatorRunner, is_public: bool) -> str:
    if is_public:
        return i18n.get("visibility-public")
    return i18n.get("visibility-private")


def _admin_keyboard(i18n: TranslatorRunner, group: Group) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                text=i18n.get("button-show-invite"),
                callback_data="group_admin:invite",
            ),
        ],
    ]
    if group.is_public:
        rows.append([
            InlineKeyboardButton(
                text=i18n.get("button-toggle-private"),
                callback_data="group_admin:private",
            ),
        ])
    else:
        rows.append([
            InlineKeyboardButton(
                text=i18n.get("button-toggle-public"),
                callback_data="group_admin:public",
            ),
        ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.callback_query(F.data.startswith("join_group:"))
async def callback_join_group(
    callback: CallbackQuery,
    i18n: TranslatorRunner,
    user: User,
    dialog_manager: DialogManager,
) -> None:
    group_id = int(callback.data.split(":")[1])
    repo = get_repository()
    group = repo.get_group(group_id)

    if not group or not group.is_public:
        await callback.answer(i18n.get("message-group-not-found"), show_alert=True)
        return

    if repo.is_blocked(group.id, user.telegram_id):
        await callback.answer(
            i18n.get("message-blocked-in-group", name=group.name),
            show_alert=True,
        )
        return

    if not repo.is_member(group.id, user.telegram_id):
        repo.add_member(group.id, user.telegram_id)
    repo.set_current_group(user.telegram_id, group.id)

    await callback.answer(i18n.get("message-joined-group", name=group.name))
    if callback.message:
        await callback.message.edit_reply_markup(reply_markup=None)
    await dialog_manager.start(state=MenuSG.group, mode=StartMode.RESET_STACK)


@router.callback_query(F.data.startswith("group_admin:"))
async def callback_group_admin(
    callback: CallbackQuery,
    i18n: TranslatorRunner,
    user: User,
    current_group: Group | None,
) -> None:
    if current_group is None or current_group.admin_id != user.telegram_id:
        await callback.answer(i18n.get("message-group-not-admin"), show_alert=True)
        return

    action = callback.data.split(":")[1]
    repo = get_repository()

    if action == "invite":
        link = make_invite_link(current_group.invite_code)
        await callback.answer()
        if callback.message:
            await callback.message.answer(
                f"{i18n.get('message-invite-link')}\n{link}",
            )
        return

    is_public = action == "public"
    try:
        updated = repo.set_group_public(current_group.id, user.telegram_id, is_public)
    except RepositoryError:
        await callback.answer(i18n.get("message-group-not-admin"), show_alert=True)
        return

    visibility = _visibility_text(i18n, updated.is_public)
    link = make_invite_link(updated.invite_code)
    await callback.answer(i18n.get("message-group-visibility-changed"))

    if callback.message:
        await callback.message.edit_text(
            i18n.get(
                "message-group-admin",
                name=updated.name,
                visibility=visibility,
                link=link,
            ),
            reply_markup=_admin_keyboard(i18n, updated),
        )
