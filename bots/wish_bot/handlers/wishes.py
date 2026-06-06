import asyncio
from datetime import datetime

from aiogram import Bot, F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram_dialog import DialogManager, StartMode
from fluentogram import TranslatorHub, TranslatorRunner

from bots.wish_bot.services import get_repository
from bots.wish_bot.services.repository import (
    CannotTakeOwnWishError,
    Group,
    NotWishAuthorError,
    NotWishTakerError,
    User,
    Wish,
    WishAlreadyTakenError,
    WishNotFoundError,
    WishStatus,
)
from bots.wish_bot.states.menu import MenuSG
from bots.wish_bot.states.wish import AddWishSG, CompleteWishSG
from bots.wish_bot.utils.menu_messages import send_main_menu_as_new_message
from bots.wish_bot.utils.notify import notify_new_wish
from bots.wish_bot.utils.send import answer_with_retry

router = Router()


def _taker_i18n(
    taker_id: int,
    fallback: TranslatorRunner,
    hub=None,
) -> TranslatorRunner:
    repo = get_repository()
    taker = repo.get_user(taker_id)
    locale = taker.locale if taker and taker.locale in ("ru", "en") else "ru"
    if hub:
        return hub.get_translator_by_locale(locale=locale)
    return fallback


def _wish_list_text(i18n: TranslatorRunner, wish: Wish) -> str:
    status_key = f"wish-status-{wish.status}"
    try:
        status_label = i18n.get(status_key)
    except Exception:
        status_label = wish.status
    return f"{wish.text}\n<i>{status_label}</i>"


def _format_datetime(dt: datetime | None) -> str:
    if not dt:
        return "—"
    return dt.strftime("%d.%m.%Y %H:%M")


def _user_display(user_id: int | None) -> tuple[str, str]:
    if not user_id:
        return "—", ""
    return _author_display(user_id)


def _build_archive_text(
    i18n: TranslatorRunner,
    user_id: int,
    group_id: int,
) -> str:
    repo = get_repository()
    my_wishes = repo.list_completed_wishes_by_author(user_id, group_id)
    fulfilled = repo.list_completed_wishes_by_taker(user_id, group_id)

    lines = [i18n.get("message-archive-title")]

    lines.append("")
    lines.append(i18n.get("message-archive-my-wishes-header"))
    if my_wishes:
        for wish in my_wishes:
            name, username_part = _user_display(wish.taken_by_id)
            lines.append(
                i18n.get(
                    "message-archive-my-item",
                    wishText=wish.text,
                    name=name,
                    usernamePart=username_part,
                    date=_format_datetime(wish.completed_at),
                ),
            )
    else:
        lines.append(i18n.get("message-archive-section-empty"))

    lines.append("")
    lines.append(i18n.get("message-archive-fulfilled-header"))
    if fulfilled:
        for wish in fulfilled:
            name, username_part = _user_display(wish.author_id)
            lines.append(
                i18n.get(
                    "message-archive-fulfilled-item",
                    wishText=wish.text,
                    name=name,
                    usernamePart=username_part,
                    date=_format_datetime(wish.completed_at),
                ),
            )
    else:
        lines.append(i18n.get("message-archive-section-empty"))

    text = "\n".join(lines)
    if len(text) > 4000:
        return text[:3990] + "\n…"
    return text


def _author_display(author_id: int) -> tuple[str, str]:
    repo = get_repository()
    author = repo.get_user(author_id)
    name = (author.first_name if author and author.first_name else "—")
    username_part = ""
    if author and author.username:
        username_part = f" (@{author.username})"
    return name, username_part


def _taken_wish_item_text(i18n: TranslatorRunner, wish: Wish) -> str:
    name, username_part = _author_display(wish.author_id)
    return i18n.get(
        "message-taken-wish-item",
        wishText=wish.text,
        name=name,
        usernamePart=username_part,
    )


def _after_take_keyboard(i18n: TranslatorRunner, wish_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.get("button-complete"),
                    callback_data=f"complete:{wish_id}",
                ),
                InlineKeyboardButton(
                    text=i18n.get("button-my-taken"),
                    callback_data="my_taken_list",
                ),
            ],
        ],
    )


def _taken_wish_keyboard(i18n: TranslatorRunner, wish_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.get("button-complete"),
                    callback_data=f"complete:{wish_id}",
                ),
            ],
        ],
    )


async def _send_my_taken_list(
    message: Message,
    i18n: TranslatorRunner,
    user_id: int,
    group_id: int,
) -> None:
    repo = get_repository()
    wishes = repo.list_taken_by_user(user_id, group_id)

    if not wishes:
        await answer_with_retry(message, i18n.get("message-no-taken-wishes"))
        return

    await answer_with_retry(message, i18n.get("message-taken-wishes-header"))

    for wish in wishes:
        await answer_with_retry(
            message,
            _taken_wish_item_text(i18n, wish),
            reply_markup=_taken_wish_keyboard(i18n, wish.id),
        )


async def prompt_add_wish(
    message: Message,
    i18n: TranslatorRunner,
    state: FSMContext,
    current_group: Group | None,
) -> None:
    if current_group is None:
        await answer_with_retry(message, i18n.get("message-no-group"))
        return
    await state.set_state(AddWishSG.waiting_text)
    await answer_with_retry(message, i18n.get("message-add-wish-prompt"))


@router.message(StateFilter(AddWishSG.waiting_text), F.text)
async def process_add_wish(
    message: Message,
    bot: Bot,
    i18n: TranslatorRunner,
    state: FSMContext,
    user: User,
    current_group: Group | None,
    dialog_manager: DialogManager,
    **kwargs,
) -> None:
    if current_group is None:
        await state.clear()
        await answer_with_retry(message, i18n.get("message-no-group"))
        return

    text = (message.text or "").strip()
    if not text:
        await answer_with_retry(message, i18n.get("message-wish-empty"))
        return

    repo = get_repository()
    wish = repo.create_wish(current_group.id, user.telegram_id, text)
    await state.clear()
    await answer_with_retry(message, i18n.get("message-wish-added"))
    await dialog_manager.start(state=MenuSG.group, mode=StartMode.RESET_STACK)

    hub: TranslatorHub | None = kwargs.get("_translator_hub")
    if hub:
        asyncio.create_task(
            notify_new_wish(bot, current_group, wish, user.telegram_id, hub),
        )


async def send_open_wishes(
    message: Message,
    i18n: TranslatorRunner,
    current_group: Group | None,
) -> None:
    if current_group is None:
        await answer_with_retry(message, i18n.get("message-no-group"))
        return
    repo = get_repository()
    wishes = repo.list_open_wishes(current_group.id)

    if not wishes:
        await answer_with_retry(message, i18n.get("message-no-open-wishes"))
        return

    await answer_with_retry(message, i18n.get("message-open-wishes-header"))

    for wish in wishes:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=i18n.get("button-take"),
                        callback_data=f"take:{wish.id}",
                    ),
                ],
            ],
        )
        await answer_with_retry(message, wish.text, reply_markup=keyboard)


def take_wish_for_user(
    user_id: int,
    group_id: int,
    wish_id: int,
) -> Wish:
    repo = get_repository()
    existing = repo.get_wish(wish_id)
    if not existing or existing.group_id != group_id:
        raise WishNotFoundError("Wish not found")
    return repo.take_wish(wish_id, user_id)


@router.callback_query(F.data.startswith("take:"))
async def callback_take_wish(
    callback: CallbackQuery,
    i18n: TranslatorRunner,
    user: User,
    current_group: Group | None,
) -> None:
    if current_group is None:
        await callback.answer(i18n.get("message-no-group"), show_alert=True)
        return

    wish_id = int(callback.data.split(":")[1])
    try:
        wish = take_wish_for_user(user.telegram_id, current_group.id, wish_id)
    except CannotTakeOwnWishError:
        await callback.answer(i18n.get("message-cannot-take-own"), show_alert=True)
        return
    except WishAlreadyTakenError:
        await callback.answer(i18n.get("message-wish-already-taken"), show_alert=True)
        return
    except WishNotFoundError:
        await callback.answer(i18n.get("message-wish-not-found"), show_alert=True)
        return

    name, username_part = _author_display(wish.author_id)
    text = i18n.get(
        "message-taken-for",
        name=name,
        usernamePart=username_part,
    )

    await callback.answer()
    if callback.message:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(
            text,
            reply_markup=_after_take_keyboard(i18n, wish.id),
        )


@router.callback_query(F.data == "my_taken_list")
async def callback_my_taken_list(
    callback: CallbackQuery,
    i18n: TranslatorRunner,
    user: User,
    current_group: Group | None,
) -> None:
    if current_group is None:
        await callback.answer(i18n.get("message-no-group"), show_alert=True)
        return

    await callback.answer()
    if callback.message:
        await _send_my_taken_list(
            callback.message,
            i18n,
            user.telegram_id,
            current_group.id,
        )


async def complete_wish_with_notify(
    bot: Bot,
    i18n: TranslatorRunner,
    taker_id: int,
    wish_id: int,
    completion_text: str,
) -> tuple[Wish, bool]:
    repo = get_repository()
    wish = repo.complete_wish(wish_id, taker_id, completion_text)
    author_text = i18n.get(
        "message-wish-completed-author",
        wishText=wish.text,
        message=completion_text,
    )
    try:
        await bot.send_message(chat_id=wish.author_id, text=author_text)
        return wish, True
    except Exception:
        return wish, False


async def delete_wish_with_notify(
    bot: Bot,
    i18n: TranslatorRunner,
    user_id: int,
    group_id: int,
    wish_id: int,
    *,
    translator_hub: TranslatorHub | None = None,
) -> Wish:
    repo = get_repository()
    existing = repo.get_wish(wish_id)
    if not existing or existing.group_id != group_id:
        raise WishNotFoundError("Wish not found")

    wish = repo.delete_wish(wish_id, user_id)

    if (
        wish.status == WishStatus.TAKEN
        and wish.taken_by_id
        and wish.taken_by_id != user_id
    ):
        taker_i18n = _taker_i18n(wish.taken_by_id, i18n, translator_hub)
        notify_text = taker_i18n.get(
            "message-wish-deleted-for-taker",
            wishText=wish.text,
        )
        try:
            await bot.send_message(chat_id=wish.taken_by_id, text=notify_text)
        except Exception:
            pass

    return wish


@router.callback_query(F.data.startswith("delete_wish:"))
async def callback_delete_wish(
    callback: CallbackQuery,
    bot: Bot,
    i18n: TranslatorRunner,
    user: User,
    current_group: Group | None,
    **kwargs,
) -> None:
    if current_group is None:
        await callback.answer(i18n.get("message-no-group"), show_alert=True)
        return

    wish_id = int(callback.data.split(":")[1])
    try:
        await delete_wish_with_notify(
            bot,
            i18n,
            user.telegram_id,
            current_group.id,
            wish_id,
            translator_hub=kwargs.get("_translator_hub"),
        )
    except NotWishAuthorError:
        await callback.answer(i18n.get("message-not-wish-author"), show_alert=True)
        return
    except WishNotFoundError:
        await callback.answer(i18n.get("message-wish-not-found"), show_alert=True)
        return

    await callback.answer(i18n.get("message-wish-deleted"))
    if callback.message:
        await callback.message.delete()


@router.callback_query(F.data.startswith("complete:"))
async def callback_complete_wish(
    callback: CallbackQuery,
    bot: Bot,
    i18n: TranslatorRunner,
    user: User,
) -> None:
    wish_id = int(callback.data.split(":")[1])
    completion_text = i18n.get("message-wish-completed-default")
    try:
        _, notified = await complete_wish_with_notify(
            bot,
            i18n,
            user.telegram_id,
            wish_id,
            completion_text,
        )
    except NotWishTakerError:
        await callback.answer(i18n.get("message-wish-not-found"), show_alert=True)
        return
    except WishNotFoundError:
        await callback.answer(i18n.get("message-wish-not-found"), show_alert=True)
        return
    except WishAlreadyTakenError:
        await callback.answer(i18n.get("message-wish-already-taken"), show_alert=True)
        return

    if not notified:
        await callback.answer(i18n.get("message-author-unreachable"), show_alert=True)
        return

    await callback.answer(i18n.get("message-wish-completed-taker"))


@router.message(StateFilter(CompleteWishSG.waiting_message))
async def process_complete_message(
    message: Message,
    bot: Bot,
    i18n: TranslatorRunner,
    state: FSMContext,
    user: User,
    dialog_manager: DialogManager,
    current_group: Group | None,
) -> None:
    data = await state.get_data()
    wish_id = data.get("wish_id")
    if not wish_id:
        await state.clear()
        return

    raw = message.text or ""
    if raw.strip() == "/skip":
        completion_text = i18n.get("message-wish-completed-default")
    elif raw.strip():
        completion_text = raw.strip()
    else:
        completion_text = i18n.get("message-wish-completed-default")

    try:
        _, notified = await complete_wish_with_notify(
            bot,
            i18n,
            user.telegram_id,
            wish_id,
            completion_text,
        )
    except WishNotFoundError:
        await answer_with_retry(message, i18n.get("message-wish-not-found"))
        await state.clear()
        return
    except WishAlreadyTakenError:
        await answer_with_retry(message, i18n.get("message-wish-already-taken"))
        await state.clear()
        return
    except NotWishTakerError:
        await answer_with_retry(message, i18n.get("message-wish-not-found"))
        await state.clear()
        return

    await state.clear()
    if not notified:
        await answer_with_retry(message, i18n.get("message-author-unreachable"))
    else:
        await answer_with_retry(message, i18n.get("message-wish-completed-taker"))

    if dialog_manager.has_context():
        await send_main_menu_as_new_message(dialog_manager)
    else:
        menu_state = MenuSG.group if current_group else MenuSG.no_group
        await dialog_manager.start(menu_state, mode=StartMode.RESET_STACK)

