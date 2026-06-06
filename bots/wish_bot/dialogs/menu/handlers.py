from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button
from fluentogram import TranslatorHub, TranslatorRunner

from bots.wish_bot.handlers.wishes import (
    _build_archive_text,
    prompt_add_wish,
    send_open_wishes,
    _send_my_taken_list,
)
from bots.wish_bot.services import get_repository
from bots.wish_bot.services.repository import (
    CannotBlockAdminError,
    CannotBlockSelfError,
    Group,
    NotGroupAdminError,
    User,
    UserNotMemberError,
)
from bots.wish_bot.states.menu import MenuSG
from bots.wish_bot.utils.bot_info import make_invite_link
from bots.wish_bot.utils.send import answer_with_retry


def _i18n(manager: DialogManager) -> TranslatorRunner:
    return manager.middleware_data["i18n"]


def _user(manager: DialogManager) -> User:
    return manager.middleware_data["user"]


def _current_group(manager: DialogManager) -> Group | None:
    return manager.middleware_data.get("current_group")


def _state(manager: DialogManager) -> FSMContext:
    return manager.middleware_data["state"]


async def _go_to_main_menu(dialog_manager: DialogManager) -> None:
    if _current_group(dialog_manager):
        await dialog_manager.switch_to(MenuSG.group)
    else:
        await dialog_manager.switch_to(MenuSG.no_group)


async def on_open_language(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
) -> None:
    current_context = dialog_manager.current_context()
    if current_context:
        dialog_manager.dialog_data["language_back_state"] = current_context.state
    await callback.answer()
    await dialog_manager.switch_to(MenuSG.language)


async def on_language_back(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
) -> None:
    await callback.answer()
    back_state = dialog_manager.dialog_data.get("language_back_state")
    if back_state:
        await dialog_manager.switch_to(back_state)
        return
    await _go_to_main_menu(dialog_manager)


async def _send_my_wishes(message: Message, i18n: TranslatorRunner, user: User, group: Group) -> None:
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    from bots.wish_bot.handlers.wishes import _wish_list_text

    repo = get_repository()
    wishes = repo.list_wishes_by_author(user.telegram_id, group.id)

    if not wishes:
        await answer_with_retry(message, i18n.get("message-no-my-wishes"))
        return

    await answer_with_retry(message, i18n.get("message-my-wishes-header"))

    for wish in wishes:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=i18n.get("button-delete"),
                        callback_data=f"delete_wish:{wish.id}",
                    ),
                ],
            ],
        )
        await answer_with_retry(
            message,
            _wish_list_text(i18n, wish),
            reply_markup=keyboard,
        )


async def on_select_my_group(
    callback: CallbackQuery,
    widget,
    dialog_manager: DialogManager,
) -> None:
    user = _user(dialog_manager)
    group_id = int(dialog_manager.item_id)
    repo = get_repository()
    group = repo.get_group(group_id)
    if not group or not repo.is_member(group_id, user.telegram_id):
        await callback.answer()
        return

    repo.set_current_group(user.telegram_id, group_id)
    dialog_manager.middleware_data["current_group"] = group
    await callback.answer()
    await dialog_manager.switch_to(MenuSG.group)


async def on_select_public_group(
    callback: CallbackQuery,
    widget,
    dialog_manager: DialogManager,
) -> None:
    i18n = _i18n(dialog_manager)
    user = _user(dialog_manager)
    group_id = int(dialog_manager.item_id)
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
    dialog_manager.middleware_data["current_group"] = group

    await callback.answer(i18n.get("message-joined-group", name=group.name))
    await dialog_manager.switch_to(MenuSG.group)


async def on_add_wish(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
) -> None:
    i18n = _i18n(dialog_manager)
    current_group = _current_group(dialog_manager)
    await callback.answer()
    if callback.message is None:
        return
    if current_group is None:
        await answer_with_retry(callback.message, i18n.get("message-no-group"))
        return
    await dialog_manager.done()
    await prompt_add_wish(callback.message, i18n, _state(dialog_manager), current_group)


async def on_my_wishes(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
) -> None:
    i18n = _i18n(dialog_manager)
    user = _user(dialog_manager)
    current_group = _current_group(dialog_manager)
    await callback.answer()
    if callback.message is None:
        return
    if current_group is None:
        await answer_with_retry(callback.message, i18n.get("message-no-group"))
        return
    await _send_my_wishes(callback.message, i18n, user, current_group)


async def on_open_wishes(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
) -> None:
    i18n = _i18n(dialog_manager)
    await callback.answer()
    if callback.message:
        await send_open_wishes(callback.message, i18n, _current_group(dialog_manager))


async def on_my_taken(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
) -> None:
    i18n = _i18n(dialog_manager)
    user = _user(dialog_manager)
    current_group = _current_group(dialog_manager)
    await callback.answer()
    if callback.message is None:
        return
    if current_group is None:
        await answer_with_retry(callback.message, i18n.get("message-no-group"))
        return
    await _send_my_taken_list(
        callback.message,
        i18n,
        user.telegram_id,
        current_group.id,
    )


async def on_subscribe_toggle(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
) -> None:
    i18n = _i18n(dialog_manager)
    user = _user(dialog_manager)
    current_group = _current_group(dialog_manager)
    if current_group is None:
        await callback.answer(i18n.get("message-no-group"), show_alert=True)
        return

    repo = get_repository()
    if repo.is_subscribed_wishes(current_group.id, user.telegram_id):
        repo.unsubscribe_wishes(current_group.id, user.telegram_id)
        await callback.answer(i18n.get("message-unsubscribed", name=current_group.name))
    else:
        try:
            repo.subscribe_wishes(current_group.id, user.telegram_id)
        except UserNotMemberError:
            await callback.answer(i18n.get("message-no-group"), show_alert=True)
            return
        await callback.answer(i18n.get("message-subscribed", name=current_group.name))

    await dialog_manager.show()


async def on_archive(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
) -> None:
    i18n = _i18n(dialog_manager)
    user = _user(dialog_manager)
    current_group = _current_group(dialog_manager)
    await callback.answer()
    if callback.message is None:
        return
    if current_group is None:
        await answer_with_retry(callback.message, i18n.get("message-no-group"))
        return
    text = _build_archive_text(i18n, user.telegram_id, current_group.id)
    await answer_with_retry(callback.message, text)


async def on_select_language(
    callback: CallbackQuery,
    widget,
    dialog_manager: DialogManager,
    item_id: str,
) -> None:
    locale = item_id
    if locale not in ("ru", "en"):
        await callback.answer()
        return

    user_id = callback.from_user.id
    repo = get_repository()
    repo.set_user_locale(user_id, locale)

    hub: TranslatorHub | None = dialog_manager.middleware_data.get("_translator_hub")
    if hub:
        dialog_manager.middleware_data["i18n"] = hub.get_translator_by_locale(locale=locale)

    i18n = _i18n(dialog_manager)
    await callback.answer(i18n.get("message-language-selected"))
    await _go_to_main_menu(dialog_manager)


async def on_create_group_name(
    message: Message,
    widget: MessageInput,
    dialog_manager: DialogManager,
) -> None:
    i18n = _i18n(dialog_manager)
    name = (message.text or "").strip()
    if not name:
        await answer_with_retry(message, i18n.get("message-create-group-name"))
        return

    dialog_manager.dialog_data["group_name"] = name
    await dialog_manager.switch_to(MenuSG.create_visibility)


async def on_create_group_public(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
) -> None:
    await _finish_create_group(callback, dialog_manager, is_public=True)


async def on_create_group_private(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
) -> None:
    await _finish_create_group(callback, dialog_manager, is_public=False)


async def _finish_create_group(
    callback: CallbackQuery,
    dialog_manager: DialogManager,
    is_public: bool,
) -> None:
    i18n = _i18n(dialog_manager)
    user = _user(dialog_manager)
    name = dialog_manager.dialog_data.get("group_name", "").strip()
    if not name:
        await callback.answer(i18n.get("message-create-group-expired"), show_alert=True)
        await dialog_manager.switch_to(MenuSG.create_name)
        return

    repo = get_repository()
    group = repo.create_group(admin_id=user.telegram_id, name=name, is_public=is_public)
    repo.set_current_group(user.telegram_id, group.id)
    dialog_manager.middleware_data["current_group"] = group
    dialog_manager.dialog_data.pop("group_name", None)

    link = make_invite_link(group.invite_code)
    await callback.answer()
    if callback.message:
        await answer_with_retry(
            callback.message,
            i18n.get("message-group-created", name=group.name, link=link),
        )
    await dialog_manager.switch_to(MenuSG.group)


async def on_member_action(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
) -> None:
    i18n = _i18n(dialog_manager)
    user = _user(dialog_manager)
    current_group = _current_group(dialog_manager)
    if current_group is None or current_group.admin_id != user.telegram_id:
        await callback.answer(i18n.get("message-group-not-admin"), show_alert=True)
        return

    target_id = int(dialog_manager.item_id)
    if target_id == current_group.admin_id:
        await callback.answer()
        return

    group_id = current_group.id
    repo = get_repository()

    if repo.is_blocked(group_id, target_id):
        try:
            repo.unblock_member(group_id, target_id, user.telegram_id)
        except NotGroupAdminError:
            await callback.answer(i18n.get("message-group-not-admin"), show_alert=True)
            return
        await callback.answer(i18n.get("message-member-unblocked"))
        await dialog_manager.show()
        return

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

    hub: TranslatorHub | None = dialog_manager.middleware_data.get("_translator_hub")
    if hub:
        from bots.wish_bot.handlers.moderation import _user_i18n

        target_i18n = _user_i18n(target_id, hub, i18n)
        bot: Bot | None = dialog_manager.middleware_data.get("bot")
        if bot:
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
    await dialog_manager.show()
