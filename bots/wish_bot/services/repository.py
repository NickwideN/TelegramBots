from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class WishStatus(StrEnum):
    OPEN = "open"
    TAKEN = "taken"
    COMPLETED = "completed"


class RepositoryError(Exception):
    """Базовая ошибка репозитория."""


class GroupNotFoundError(RepositoryError):
    pass


class WishNotFoundError(RepositoryError):
    pass


class WishAlreadyTakenError(RepositoryError):
    pass


class CannotTakeOwnWishError(RepositoryError):
    pass


class NotWishTakerError(RepositoryError):
    pass


class NotWishAuthorError(RepositoryError):
    pass


class UserNotMemberError(RepositoryError):
    pass


class NotGroupAdminError(RepositoryError):
    pass


class UserBlockedInGroupError(RepositoryError):
    pass


class CannotBlockSelfError(RepositoryError):
    pass


class CannotBlockAdminError(RepositoryError):
    pass


class StorageNotConfiguredError(RepositoryError):
    pass


@dataclass
class User:
    telegram_id: int
    username: str | None
    first_name: str | None
    locale: str
    current_group_id: int | None
    created_at: datetime


@dataclass
class Group:
    id: int
    name: str
    invite_code: str
    is_public: bool
    admin_id: int
    created_at: datetime


@dataclass
class Wish:
    id: int
    group_id: int
    author_id: int
    text: str
    status: WishStatus
    taken_by_id: int | None
    taken_at: datetime | None
    completed_at: datetime | None
    completion_message: str | None
    deleted: bool = False


@dataclass
class OpenWish:
    """Желание без данных автора — для анонимного списка."""

    id: int
    text: str


class Repository(ABC):
    @abstractmethod
    def upsert_user(
        self,
        telegram_id: int,
        username: str | None,
        first_name: str | None,
        locale: str | None = None,
    ) -> User:
        pass

    @abstractmethod
    def get_user(self, telegram_id: int) -> User | None:
        pass

    @abstractmethod
    def set_user_locale(self, telegram_id: int, locale: str) -> None:
        pass

    @abstractmethod
    def set_current_group(self, telegram_id: int, group_id: int | None) -> None:
        pass

    @abstractmethod
    def create_group(self, admin_id: int, name: str, is_public: bool) -> Group:
        pass

    @abstractmethod
    def get_group(self, group_id: int) -> Group | None:
        pass

    @abstractmethod
    def get_group_by_invite(self, invite_code: str) -> Group | None:
        pass

    @abstractmethod
    def list_public_groups(self) -> list[Group]:
        pass

    @abstractmethod
    def is_member(self, group_id: int, user_id: int) -> bool:
        pass

    @abstractmethod
    def add_member(self, group_id: int, user_id: int) -> None:
        pass

    @abstractmethod
    def remove_member(self, group_id: int, user_id: int) -> None:
        pass

    @abstractmethod
    def list_group_members(self, group_id: int) -> list[int]:
        pass

    @abstractmethod
    def is_blocked(self, group_id: int, user_id: int) -> bool:
        pass

    @abstractmethod
    def list_blocked_members(self, group_id: int) -> list[int]:
        pass

    @abstractmethod
    def block_member(self, group_id: int, user_id: int, admin_id: int) -> None:
        pass

    @abstractmethod
    def unblock_member(self, group_id: int, user_id: int, admin_id: int) -> None:
        pass

    @abstractmethod
    def set_group_public(self, group_id: int, admin_id: int, is_public: bool) -> Group:
        pass

    @abstractmethod
    def create_wish(self, group_id: int, author_id: int, text: str) -> Wish:
        pass

    @abstractmethod
    def list_open_wishes(self, group_id: int) -> list[OpenWish]:
        pass

    @abstractmethod
    def get_wish(self, wish_id: int) -> Wish | None:
        pass

    @abstractmethod
    def take_wish(self, wish_id: int, taker_id: int) -> Wish:
        pass

    @abstractmethod
    def list_taken_by_user(self, user_id: int, group_id: int) -> list[Wish]:
        pass

    @abstractmethod
    def complete_wish(self, wish_id: int, taker_id: int, message: str) -> Wish:
        pass

    @abstractmethod
    def list_wishes_by_author(self, author_id: int, group_id: int) -> list[Wish]:
        pass

    @abstractmethod
    def delete_wish(self, wish_id: int, author_id: int) -> Wish:
        pass

    @abstractmethod
    def subscribe_wishes(self, group_id: int, user_id: int) -> None:
        pass

    @abstractmethod
    def unsubscribe_wishes(self, group_id: int, user_id: int) -> None:
        pass

    @abstractmethod
    def is_subscribed_wishes(self, group_id: int, user_id: int) -> bool:
        pass

    @abstractmethod
    def list_wish_subscribers(self, group_id: int) -> list[int]:
        pass

    @abstractmethod
    def list_completed_wishes_by_author(self, author_id: int, group_id: int) -> list[Wish]:
        pass

    @abstractmethod
    def list_completed_wishes_by_taker(self, taker_id: int, group_id: int) -> list[Wish]:
        pass
