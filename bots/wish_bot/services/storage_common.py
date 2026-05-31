"""Общие хелперы для SQLite и Postgres."""

import secrets
import string
from datetime import datetime, timezone
from typing import Any, Mapping

from bots.wish_bot.services.repository import Group, OpenWish, User, Wish, WishStatus

WISH_NOT_DELETED = "deleted = 0"


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def generate_invite_code(length: int = 10) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def to_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value)
    raise TypeError(f"Unsupported datetime value: {value!r}")


def row_to_user(row: Mapping[str, Any]) -> User:
    return User(
        telegram_id=row["telegram_id"],
        username=row["username"],
        first_name=row["first_name"],
        locale=row["locale"],
        current_group_id=row["current_group_id"],
        created_at=to_datetime(row["created_at"]) or utcnow(),
    )


def row_to_group(row: Mapping[str, Any]) -> Group:
    is_public = row["is_public"]
    if isinstance(is_public, int):
        is_public = bool(is_public)
    return Group(
        id=row["id"],
        name=row["name"],
        invite_code=row["invite_code"],
        is_public=is_public,
        admin_id=row["admin_id"],
        created_at=to_datetime(row["created_at"]) or utcnow(),
    )


def row_to_wish(row: Mapping[str, Any]) -> Wish:
    deleted = row["deleted"]
    if isinstance(deleted, int):
        deleted = bool(deleted)
    return Wish(
        id=row["id"],
        group_id=row["group_id"],
        author_id=row["author_id"],
        text=row["text"],
        status=WishStatus(row["status"]),
        taken_by_id=row["taken_by_id"],
        taken_at=to_datetime(row["taken_at"]),
        completed_at=to_datetime(row["completed_at"]),
        completion_message=row["completion_message"],
        deleted=deleted,
    )
