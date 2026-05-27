"""Кэш username бота для invite-ссылок."""

_bot_username: str | None = None


def set_bot_username(username: str) -> None:
    global _bot_username
    _bot_username = username


def get_bot_username() -> str | None:
    return _bot_username


def make_invite_link(invite_code: str) -> str:
    username = _bot_username
    if not username:
        return f"?start=join_{invite_code}"
    return f"https://t.me/{username}?start=join_{invite_code}"
