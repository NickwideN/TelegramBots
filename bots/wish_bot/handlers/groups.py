from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from fluentogram import TranslatorRunner

from bots.wish_bot.handlers.commands import send_join_welcome
from bots.wish_bot.services import get_repository
from bots.wish_bot.handlers.moderation import _send_blocked_list, _send_members_list
from bots.wish_bot.services.repository import Group, RepositoryError, User
from bots.wish_bot.states.group import CreateGroupSG
from bots.wish_bot.utils.bot_info import make_invite_link
from bots.wish_bot.utils.send import answer_with_retry

router = Router()


def _visibility_text(i18n: TranslatorRunner, is_public: bool) -> str:
    if is_public:
        return i18n.get("visibility-public")
    return i18n.get("visibility-private")


def _visibility_keyboard(i18n: TranslatorRunner) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.get("button-public"),
                    callback_data="create_group:public",
                ),
                InlineKeyboardButton(
                    text=i18n.get("button-private"),
                    callback_data="create_group:private",
                ),
            ],
        ],
    )


def _admin_keyboard(i18n: TranslatorRunner, group: Group) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                text=i18n.get("button-show-invite"),
                callback_data="group_admin:invite",
            ),
        ],
        [
            InlineKeyboardButton(
                text=i18n.get("button-group-members"),
                callback_data="group_admin:members",
            ),
            InlineKeyboardButton(
                text=i18n.get("button-group-blocked"),
                callback_data="group_admin:blocked",
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


async def prompt_create_group(
    message: Message,
    i18n: TranslatorRunner,
    state: FSMContext,
) -> None:
    await state.clear()
    await state.set_state(CreateGroupSG.waiting_name)
    await answer_with_retry(message, i18n.get("message-create-group-name"))


@router.message(Command(commands=["create_group"]))
async def cmd_create_group(message: Message, i18n: TranslatorRunner, state: FSMContext) -> None:
    """Создание группы — ввод названия."""
    await prompt_create_group(message, i18n, state)


@router.callback_query(F.data == "menu:create_group")
async def callback_menu_create_group(
    callback: CallbackQuery,
    i18n: TranslatorRunner,
    state: FSMContext,
) -> None:
    await callback.answer()
    if callback.message:
        await prompt_create_group(callback.message, i18n, state)


@router.message(StateFilter(CreateGroupSG.waiting_name), F.text)
async def process_group_name(message: Message, i18n: TranslatorRunner, state: FSMContext) -> None:
    name = (message.text or "").strip()
    if not name:
        await answer_with_retry(message, i18n.get("message-create-group-name"))
        return

    await state.update_data(group_name=name)
    await state.set_state(CreateGroupSG.waiting_visibility)
    prompt = await answer_with_retry(
        message,
        i18n.get("message-create-group-visibility"),
        reply_markup=_visibility_keyboard(i18n),
    )
    await state.update_data(
        visibility_message_id=prompt.message_id,
        visibility_chat_id=prompt.chat.id,
    )


@router.callback_query(
    StateFilter(CreateGroupSG.waiting_visibility),
    F.data.in_(("create_group:public", "create_group:private")),
)
async def process_group_visibility(
    callback: CallbackQuery,
    i18n: TranslatorRunner,
    state: FSMContext,
    user: User,
) -> None:
    data = await state.get_data()
    if (
        callback.message
        and data.get("visibility_message_id") != callback.message.message_id
    ):
        await callback.answer(
            i18n.get("message-create-group-expired"),
            show_alert=True,
        )
        return

    is_public = callback.data == "create_group:public"
    name = data.get("group_name", "")
    await state.clear()

    repo = get_repository()
    group = repo.create_group(admin_id=user.telegram_id, name=name, is_public=is_public)
    repo.set_current_group(user.telegram_id, group.id)

    link = make_invite_link(group.invite_code)
    text = i18n.get("message-group-created", name=group.name, link=link)

    if callback.message:
        await callback.message.edit_text(text)
    await callback.answer()


@router.callback_query(F.data.in_(("create_group:public", "create_group:private")))
async def stale_create_group_visibility(
    callback: CallbackQuery,
    i18n: TranslatorRunner,
) -> None:
    await callback.answer(
        i18n.get("message-create-group-expired"),
        show_alert=True,
    )
    if callback.message:
        await callback.message.edit_reply_markup(reply_markup=None)


@router.message(Command(commands=["group"]))
async def cmd_group(
    message: Message,
    i18n: TranslatorRunner,
    user: User,
    current_group: Group | None,
) -> None:
    """Текущая группа."""
    if current_group is None:
        await answer_with_retry(message, i18n.get("message-no-group"))
        return

    visibility = _visibility_text(i18n, current_group.is_public)
    if current_group.admin_id == user.telegram_id:
        link = make_invite_link(current_group.invite_code)
        text = i18n.get(
            "message-current-group-admin",
            name=current_group.name,
            visibility=visibility,
            link=link,
        )
    else:
        text = i18n.get(
            "message-current-group",
            name=current_group.name,
            visibility=visibility,
        )
    await answer_with_retry(message, text)


async def send_public_groups(
    message: Message,
    i18n: TranslatorRunner,
    user: User,
) -> None:
    repo = get_repository()
    groups = repo.list_public_groups()

    joinable = [
        g for g in groups
        if not repo.is_member(g.id, user.telegram_id)
        and not repo.is_blocked(g.id, user.telegram_id)
    ]

    if not joinable:
        await answer_with_retry(message, i18n.get("message-no-public-groups"))
        return

    for group in joinable:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=i18n.get("button-join-group", name=group.name),
                        callback_data=f"join_group:{group.id}",
                    ),
                ],
            ],
        )
        await answer_with_retry(message, group.name, reply_markup=keyboard)


@router.message(Command(commands=["groups"]))
async def cmd_groups(message: Message, i18n: TranslatorRunner, user: User) -> None:
    """Список публичных групп."""
    await send_public_groups(message, i18n, user)


@router.callback_query(F.data == "menu:groups")
async def callback_menu_groups(
    callback: CallbackQuery,
    i18n: TranslatorRunner,
    user: User,
) -> None:
    await callback.answer()
    if callback.message:
        await send_public_groups(callback.message, i18n, user)


@router.callback_query(F.data.startswith("join_group:"))
async def callback_join_group(
    callback: CallbackQuery,
    i18n: TranslatorRunner,
    user: User,
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

    await callback.answer()
    if callback.message:
        await callback.message.edit_reply_markup(reply_markup=None)
        await send_join_welcome(callback.message, i18n, group.name)


@router.message(Command(commands=["group_admin"]))
async def cmd_group_admin(
    message: Message,
    i18n: TranslatorRunner,
    user: User,
    current_group: Group | None,
) -> None:
    """Настройки группы для администратора."""
    if current_group is None:
        await answer_with_retry(message, i18n.get("message-no-group"))
        return

    if current_group.admin_id != user.telegram_id:
        await answer_with_retry(message, i18n.get("message-group-not-admin"))
        return

    visibility = _visibility_text(i18n, current_group.is_public)
    link = make_invite_link(current_group.invite_code)
    await answer_with_retry(
        message,
        i18n.get(
            "message-group-admin",
            name=current_group.name,
            visibility=visibility,
            link=link,
        ),
        reply_markup=_admin_keyboard(i18n, current_group),
    )


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

    if action == "members":
        await callback.answer()
        if callback.message:
            await _send_members_list(callback.message, i18n, current_group)
        return

    if action == "blocked":
        await callback.answer()
        if callback.message:
            await _send_blocked_list(callback.message, i18n, current_group)
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
