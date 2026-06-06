from bots.wish_bot.services import get_repository


def _member_user(user_id: int):
    return get_repository().get_user(user_id)


def member_short_name(user_id: int) -> str:
    member = _member_user(user_id)
    if not member:
        return str(user_id)
    return member.first_name or "—"


def member_label(user_id: int) -> str:
    member = _member_user(user_id)
    if not member:
        return str(user_id)
    name = member.first_name or "—"
    username_part = f" (@{member.username})" if member.username else ""
    return f"{name}{username_part}"


def member_display_name(user_id: int) -> str:
    return member_label(user_id)
