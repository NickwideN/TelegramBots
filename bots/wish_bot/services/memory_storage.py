import secrets
import string
from datetime import datetime, timezone

from bots.wish_bot.services.repository import (
    CannotTakeOwnWishError,
    Group,
    GroupNotFoundError,
    NotWishAuthorError,
    NotWishTakerError,
    OpenWish,
    Repository,
    RepositoryError,
    User,
    CannotBlockAdminError,
    CannotBlockSelfError,
    NotGroupAdminError,
    UserBlockedInGroupError,
    UserNotMemberError,
    Wish,
    WishAlreadyTakenError,
    WishNotFoundError,
    WishStatus,
)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _generate_invite_code(length: int = 10) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


class MemoryStorage(Repository):
    def __init__(self) -> None:
        self._users: dict[int, User] = {}
        self._groups: dict[int, Group] = {}
        self._members: set[tuple[int, int]] = set()
        self._wishes: dict[int, Wish] = {}
        self._invite_index: dict[str, int] = {}
        self._next_group_id = 1
        self._next_wish_id = 1
        self._wish_subscriptions: set[tuple[int, int]] = set()
        self._blocks: set[tuple[int, int]] = set()

    def upsert_user(
        self,
        telegram_id: int,
        username: str | None,
        first_name: str | None,
        locale: str | None = None,
    ) -> User:
        existing = self._users.get(telegram_id)
        if existing:
            self._users[telegram_id] = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                locale=locale or existing.locale,
                current_group_id=existing.current_group_id,
                created_at=existing.created_at,
            )
            return self._users[telegram_id]

        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            locale=locale or "ru",
            current_group_id=None,
            created_at=_utcnow(),
        )
        self._users[telegram_id] = user
        return user

    def get_user(self, telegram_id: int) -> User | None:
        return self._users.get(telegram_id)

    def set_user_locale(self, telegram_id: int, locale: str) -> None:
        user = self._users.get(telegram_id)
        if user:
            self._users[telegram_id] = User(
                telegram_id=user.telegram_id,
                username=user.username,
                first_name=user.first_name,
                locale=locale,
                current_group_id=user.current_group_id,
                created_at=user.created_at,
            )

    def set_current_group(self, telegram_id: int, group_id: int | None) -> None:
        user = self._users.get(telegram_id)
        if not user:
            raise UserNotMemberError("User not found")
        self._users[telegram_id] = User(
            telegram_id=user.telegram_id,
            username=user.username,
            first_name=user.first_name,
            locale=user.locale,
            current_group_id=group_id,
            created_at=user.created_at,
        )

    def create_group(self, admin_id: int, name: str, is_public: bool) -> Group:
        group_id = self._next_group_id
        self._next_group_id += 1

        invite_code = _generate_invite_code()
        while invite_code in self._invite_index:
            invite_code = _generate_invite_code()

        group = Group(
            id=group_id,
            name=name,
            invite_code=invite_code,
            is_public=is_public,
            admin_id=admin_id,
            created_at=_utcnow(),
        )
        self._groups[group_id] = group
        self._invite_index[invite_code] = group_id
        self._members.add((group_id, admin_id))
        return group

    def get_group(self, group_id: int) -> Group | None:
        return self._groups.get(group_id)

    def get_group_by_invite(self, invite_code: str) -> Group | None:
        group_id = self._invite_index.get(invite_code)
        if group_id is None:
            return None
        return self._groups.get(group_id)

    def list_public_groups(self) -> list[Group]:
        return [g for g in self._groups.values() if g.is_public]

    def is_member(self, group_id: int, user_id: int) -> bool:
        return (group_id, user_id) in self._members

    def add_member(self, group_id: int, user_id: int) -> None:
        if group_id not in self._groups:
            raise GroupNotFoundError("Group not found")
        if self.is_blocked(group_id, user_id):
            raise UserBlockedInGroupError("User is blocked in this group")
        self._members.add((group_id, user_id))

    def remove_member(self, group_id: int, user_id: int) -> None:
        self._members.discard((group_id, user_id))

    def list_group_members(self, group_id: int) -> list[int]:
        return sorted(
            uid for gid, uid in self._members if gid == group_id
        )

    def is_blocked(self, group_id: int, user_id: int) -> bool:
        return (group_id, user_id) in self._blocks

    def list_blocked_members(self, group_id: int) -> list[int]:
        return sorted(uid for gid, uid in self._blocks if gid == group_id)

    def block_member(self, group_id: int, user_id: int, admin_id: int) -> None:
        group = self._groups.get(group_id)
        if not group:
            raise GroupNotFoundError("Group not found")
        if group.admin_id != admin_id:
            raise NotGroupAdminError("Not group admin")
        if user_id == admin_id:
            raise CannotBlockSelfError("Cannot block yourself")
        if user_id == group.admin_id:
            raise CannotBlockAdminError("Cannot block group admin")
        if not self.is_member(group_id, user_id):
            raise UserNotMemberError("Not a group member")

        self._blocks.add((group_id, user_id))
        self.remove_member(group_id, user_id)
        self.unsubscribe_wishes(group_id, user_id)
        member = self._users.get(user_id)
        if member and member.current_group_id == group_id:
            self.set_current_group(user_id, None)

    def unblock_member(self, group_id: int, user_id: int, admin_id: int) -> None:
        group = self._groups.get(group_id)
        if not group:
            raise GroupNotFoundError("Group not found")
        if group.admin_id != admin_id:
            raise NotGroupAdminError("Not group admin")
        self._blocks.discard((group_id, user_id))

    def set_group_public(self, group_id: int, admin_id: int, is_public: bool) -> Group:
        group = self._groups.get(group_id)
        if not group:
            raise GroupNotFoundError("Group not found")
        if group.admin_id != admin_id:
            raise RepositoryError("Not group admin")

        updated = Group(
            id=group.id,
            name=group.name,
            invite_code=group.invite_code,
            is_public=is_public,
            admin_id=group.admin_id,
            created_at=group.created_at,
        )
        self._groups[group_id] = updated
        return updated

    def create_wish(self, group_id: int, author_id: int, text: str) -> Wish:
        if group_id not in self._groups:
            raise GroupNotFoundError("Group not found")
        if not self.is_member(group_id, author_id):
            raise UserNotMemberError("Not a group member")

        wish_id = self._next_wish_id
        self._next_wish_id += 1
        wish = Wish(
            id=wish_id,
            group_id=group_id,
            author_id=author_id,
            text=text,
            status=WishStatus.OPEN,
            taken_by_id=None,
            taken_at=None,
            completed_at=None,
            completion_message=None,
            deleted=False,
        )
        self._wishes[wish_id] = wish
        return wish

    def list_open_wishes(self, group_id: int) -> list[OpenWish]:
        return [
            OpenWish(id=w.id, text=w.text)
            for w in self._wishes.values()
            if w.group_id == group_id
            and w.status == WishStatus.OPEN
            and not w.deleted
        ]

    def get_wish(self, wish_id: int) -> Wish | None:
        wish = self._wishes.get(wish_id)
        if wish and wish.deleted:
            return None
        return wish

    def take_wish(self, wish_id: int, taker_id: int) -> Wish:
        wish = self._wishes.get(wish_id)
        if not wish or wish.deleted:
            raise WishNotFoundError("Wish not found")
        if wish.status != WishStatus.OPEN:
            raise WishAlreadyTakenError("Wish already taken")
        if wish.author_id == taker_id:
            raise CannotTakeOwnWishError("Cannot take own wish")
        if not self.is_member(wish.group_id, taker_id):
            raise UserNotMemberError("Not a group member")

        updated = Wish(
            id=wish.id,
            group_id=wish.group_id,
            author_id=wish.author_id,
            text=wish.text,
            status=WishStatus.TAKEN,
            taken_by_id=taker_id,
            taken_at=_utcnow(),
            completed_at=None,
            completion_message=None,
            deleted=False,
        )
        self._wishes[wish_id] = updated
        return updated

    def list_taken_by_user(self, user_id: int, group_id: int) -> list[Wish]:
        return [
            w
            for w in self._wishes.values()
            if w.group_id == group_id
            and w.status == WishStatus.TAKEN
            and w.taken_by_id == user_id
            and not w.deleted
        ]

    def complete_wish(self, wish_id: int, taker_id: int, message: str) -> Wish:
        wish = self._wishes.get(wish_id)
        if not wish or wish.deleted:
            raise WishNotFoundError("Wish not found")
        if wish.taken_by_id != taker_id:
            raise NotWishTakerError("Not the wish taker")
        if wish.status != WishStatus.TAKEN:
            raise WishAlreadyTakenError("Wish is not in taken state")

        updated = Wish(
            id=wish.id,
            group_id=wish.group_id,
            author_id=wish.author_id,
            text=wish.text,
            status=WishStatus.COMPLETED,
            taken_by_id=wish.taken_by_id,
            taken_at=wish.taken_at,
            completed_at=_utcnow(),
            completion_message=message,
            deleted=wish.deleted,
        )
        self._wishes[wish_id] = updated
        return updated

    def list_wishes_by_author(self, author_id: int, group_id: int) -> list[Wish]:
        return sorted(
            [
                w
                for w in self._wishes.values()
                if w.group_id == group_id
                and w.author_id == author_id
                and not w.deleted
            ],
            key=lambda w: w.id,
        )

    def delete_wish(self, wish_id: int, author_id: int) -> Wish:
        wish = self._wishes.get(wish_id)
        if not wish or wish.deleted:
            raise WishNotFoundError("Wish not found")
        if wish.author_id != author_id:
            raise NotWishAuthorError("Not the wish author")

        updated = Wish(
            id=wish.id,
            group_id=wish.group_id,
            author_id=wish.author_id,
            text=wish.text,
            status=wish.status,
            taken_by_id=wish.taken_by_id,
            taken_at=wish.taken_at,
            completed_at=wish.completed_at,
            completion_message=wish.completion_message,
            deleted=True,
        )
        self._wishes[wish_id] = updated
        return wish

    def subscribe_wishes(self, group_id: int, user_id: int) -> None:
        if group_id not in self._groups:
            raise GroupNotFoundError("Group not found")
        if not self.is_member(group_id, user_id):
            raise UserNotMemberError("Not a group member")
        self._wish_subscriptions.add((group_id, user_id))

    def unsubscribe_wishes(self, group_id: int, user_id: int) -> None:
        self._wish_subscriptions.discard((group_id, user_id))

    def is_subscribed_wishes(self, group_id: int, user_id: int) -> bool:
        return (group_id, user_id) in self._wish_subscriptions

    def list_wish_subscribers(self, group_id: int) -> list[int]:
        return sorted(
            uid for gid, uid in self._wish_subscriptions if gid == group_id
        )
