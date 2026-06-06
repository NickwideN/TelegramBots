from bots.wish_bot.services import get_repository


def member_label(user_id: int) -> str:
    repo = get_repository()
    member = repo.get_user(user_id)
    if not member:
        return str(user_id)
    name = member.first_name or "—"
    username_part = f" (@{member.username})" if member.username else ""
    return f"{name}{username_part}"
