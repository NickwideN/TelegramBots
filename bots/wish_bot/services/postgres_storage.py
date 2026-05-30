"""Postgres-реализация репозитория — подключить после настройки Heroku Postgres."""

from bots.wish_bot.services.repository import (
    Group,
    OpenWish,
    Repository,
    StorageNotConfiguredError,
    User,
    Wish,
)


class PostgresStorage(Repository):
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url
        raise StorageNotConfiguredError(
            "Postgres storage is not implemented yet. Use WISH_BOT_STORAGE=memory."
        )

    def upsert_user(self, telegram_id: int, username: str | None, first_name: str | None, locale: str | None = None) -> User:
        raise StorageNotConfiguredError()

    def get_user(self, telegram_id: int) -> User | None:
        raise StorageNotConfiguredError()

    def set_user_locale(self, telegram_id: int, locale: str) -> None:
        raise StorageNotConfiguredError()

    def set_current_group(self, telegram_id: int, group_id: int | None) -> None:
        raise StorageNotConfiguredError()

    def create_group(self, admin_id: int, name: str, is_public: bool) -> Group:
        raise StorageNotConfiguredError()

    def get_group(self, group_id: int) -> Group | None:
        raise StorageNotConfiguredError()

    def get_group_by_invite(self, invite_code: str) -> Group | None:
        raise StorageNotConfiguredError()

    def list_public_groups(self) -> list[Group]:
        raise StorageNotConfiguredError()

    def is_member(self, group_id: int, user_id: int) -> bool:
        raise StorageNotConfiguredError()

    def add_member(self, group_id: int, user_id: int) -> None:
        raise StorageNotConfiguredError()

    def remove_member(self, group_id: int, user_id: int) -> None:
        raise StorageNotConfiguredError()

    def list_group_members(self, group_id: int) -> list[int]:
        raise StorageNotConfiguredError()

    def is_blocked(self, group_id: int, user_id: int) -> bool:
        raise StorageNotConfiguredError()

    def list_blocked_members(self, group_id: int) -> list[int]:
        raise StorageNotConfiguredError()

    def block_member(self, group_id: int, user_id: int, admin_id: int) -> None:
        raise StorageNotConfiguredError()

    def unblock_member(self, group_id: int, user_id: int, admin_id: int) -> None:
        raise StorageNotConfiguredError()

    def set_group_public(self, group_id: int, admin_id: int, is_public: bool) -> Group:
        raise StorageNotConfiguredError()

    def create_wish(self, group_id: int, author_id: int, text: str) -> Wish:
        raise StorageNotConfiguredError()

    def list_open_wishes(self, group_id: int) -> list[OpenWish]:
        raise StorageNotConfiguredError()

    def get_wish(self, wish_id: int) -> Wish | None:
        raise StorageNotConfiguredError()

    def take_wish(self, wish_id: int, taker_id: int) -> Wish:
        raise StorageNotConfiguredError()

    def list_taken_by_user(self, user_id: int, group_id: int) -> list[Wish]:
        raise StorageNotConfiguredError()

    def complete_wish(self, wish_id: int, taker_id: int, message: str) -> Wish:
        raise StorageNotConfiguredError()

    def list_wishes_by_author(self, author_id: int, group_id: int) -> list[Wish]:
        raise StorageNotConfiguredError()

    def delete_wish(self, wish_id: int, author_id: int) -> Wish:
        raise StorageNotConfiguredError()

    def subscribe_wishes(self, group_id: int, user_id: int) -> None:
        raise StorageNotConfiguredError()

    def unsubscribe_wishes(self, group_id: int, user_id: int) -> None:
        raise StorageNotConfiguredError()

    def is_subscribed_wishes(self, group_id: int, user_id: int) -> bool:
        raise StorageNotConfiguredError()

    def list_wish_subscribers(self, group_id: int) -> list[int]:
        raise StorageNotConfiguredError()

    def list_completed_wishes_by_author(self, author_id: int, group_id: int) -> list[Wish]:
        raise StorageNotConfiguredError()

    def list_completed_wishes_by_taker(self, taker_id: int, group_id: int) -> list[Wish]:
        raise StorageNotConfiguredError()
