import logging

from aiogram import F, Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from fluentogram import TranslatorHub, TranslatorRunner

from bots.wish_bot.services import get_repository
from bots.wish_bot.utils.bot_info import make_invite_link
from bots.wish_bot.utils.share import build_share_invite_text

logger = logging.getLogger(__name__)

router = Router()

_SHARE_PREFIX = "share_"


def _user_i18n(user_id: int, hub: TranslatorHub) -> TranslatorRunner:
    repo = get_repository()
    user = repo.get_user(user_id)
    locale = user.locale if user and user.locale in ("ru", "en") else "ru"
    return hub.get_translator_by_locale(locale=locale)


def _can_share_group(group, user_id: int) -> bool:
    repo = get_repository()
    if not repo.is_member(group.id, user_id):
        return False
    if group.is_public:
        return True
    return group.admin_id == user_id


@router.inline_query(F.query.startswith(_SHARE_PREFIX))
async def inline_share_group(
    inline_query: InlineQuery,
    _translator_hub: TranslatorHub,
) -> None:
    invite_code = inline_query.query[len(_SHARE_PREFIX):]
    if not invite_code or inline_query.from_user is None:
        await inline_query.answer([], cache_time=0, is_personal=True)
        return

    repo = get_repository()
    group = repo.get_group_by_invite(invite_code)
    user_id = inline_query.from_user.id

    if not group:
        logger.warning("inline share: group not found for invite_code=%s", invite_code)
        await inline_query.answer([], cache_time=0, is_personal=True)
        return

    if not _can_share_group(group, user_id):
        logger.warning(
            "inline share: denied user_id=%s group_id=%s public=%s admin_id=%s",
            user_id,
            group.id,
            group.is_public,
            group.admin_id,
        )
        await inline_query.answer([], cache_time=0, is_personal=True)
        return

    i18n = _user_i18n(user_id, _translator_hub)
    link = make_invite_link(group.invite_code)
    message_text = build_share_invite_text(i18n, group, link)

    result = InlineQueryResultArticle(
        id=f"share_{group.id}",
        title=i18n.get("button-share"),
        description=group.name,
        input_message_content=InputTextMessageContent(message_text=message_text),
    )
    await inline_query.answer([result], cache_time=0, is_personal=True)
