from urllib.parse import quote

from fluentogram import TranslatorRunner

from bots.wish_bot.services.repository import Group

_BIDI_MARKS = ("\u2068", "\u2069")


def _clean_share_text(text: str) -> str:
    for mark in _BIDI_MARKS:
        text = text.replace(mark, "")
    return text


def build_share_invite_text(i18n: TranslatorRunner, group: Group, link: str) -> str:
    if group.is_public:
        key = "message-share-invite-public"
    else:
        key = "message-share-invite-private"
    return _clean_share_text(i18n.get(key, name=group.name, link=link))


def build_share_invite_body(i18n: TranslatorRunner, group: Group) -> str:
    if group.is_public:
        key = "message-share-invite-public-body"
    else:
        key = "message-share-invite-private-body"
    return _clean_share_text(i18n.get(key, name=group.name))


def make_telegram_share_url(invite_link: str, message_text: str) -> str:
    return (
        "https://t.me/share/url?"
        f"url={quote(invite_link, safe='')}"
        f"&text={quote(message_text, safe='')}"
    )
