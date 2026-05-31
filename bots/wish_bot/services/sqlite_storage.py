import sqlite3
from pathlib import Path

from bots.wish_bot.services.repository import (
    CannotBlockAdminError,
    CannotBlockSelfError,
    CannotTakeOwnWishError,
    Group,
    GroupNotFoundError,
    NotGroupAdminError,
    NotWishAuthorError,
    NotWishTakerError,
    OpenWish,
    Repository,
    RepositoryError,
    User,
    UserBlockedInGroupError,
    UserNotMemberError,
    Wish,
    WishAlreadyTakenError,
    WishNotFoundError,
    WishStatus,
)
from bots.wish_bot.services.storage_common import (
    WISH_NOT_DELETED,
    generate_invite_code,
    row_to_group,
    row_to_user,
    row_to_wish,
    utcnow,
)

_SCHEMA_PATH = Path(__file__).parent / "schema.sqlite.sql"


class SqliteStorage(Repository):
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _database_initialized(self, conn: sqlite3.Connection) -> bool:
        row = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'users'",
        ).fetchone()
        return row is not None

    def _init_db(self) -> None:
        with self._connect() as conn:
            if self._database_initialized(conn):
                return
            conn.executescript(_SCHEMA_PATH.read_text(encoding="utf-8"))

    def upsert_user(
        self,
        telegram_id: int,
        username: str | None,
        first_name: str | None,
        locale: str | None = None,
    ) -> User:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE telegram_id = ?",
                (telegram_id,),
            ).fetchone()

            if row:
                new_locale = locale or row["locale"]
                conn.execute(
                    """
                    UPDATE users
                    SET username = ?, first_name = ?, locale = ?
                    WHERE telegram_id = ?
                    """,
                    (username, first_name, new_locale, telegram_id),
                )
            else:
                conn.execute(
                    """
                    INSERT INTO users (telegram_id, username, first_name, locale, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (telegram_id, username, first_name, locale or "ru", utcnow().isoformat()),
                )

            updated = conn.execute(
                "SELECT * FROM users WHERE telegram_id = ?",
                (telegram_id,),
            ).fetchone()
            return self.row_to_user(updated)

    def get_user(self, telegram_id: int) -> User | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE telegram_id = ?",
                (telegram_id,),
            ).fetchone()
            return self.row_to_user(row) if row else None

    def set_user_locale(self, telegram_id: int, locale: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE users SET locale = ? WHERE telegram_id = ?",
                (locale, telegram_id),
            )

    def set_current_group(self, telegram_id: int, group_id: int | None) -> None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT telegram_id FROM users WHERE telegram_id = ?",
                (telegram_id,),
            ).fetchone()
            if not row:
                raise UserNotMemberError("User not found")
            conn.execute(
                "UPDATE users SET current_group_id = ? WHERE telegram_id = ?",
                (group_id, telegram_id),
            )

    def create_group(self, admin_id: int, name: str, is_public: bool) -> Group:
        invite_code = generate_invite_code()
        now = utcnow().isoformat()

        with self._connect() as conn:
            while conn.execute(
                "SELECT 1 FROM groups WHERE invite_code = ?",
                (invite_code,),
            ).fetchone():
                invite_code = generate_invite_code()

            cursor = conn.execute(
                """
                INSERT INTO groups (name, invite_code, is_public, admin_id, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (name, invite_code, int(is_public), admin_id, now),
            )
            group_id = cursor.lastrowid
            conn.execute(
                """
                INSERT OR IGNORE INTO group_members (group_id, user_id, joined_at)
                VALUES (?, ?, ?)
                """,
                (group_id, admin_id, now),
            )
            row = conn.execute(
                "SELECT * FROM groups WHERE id = ?",
                (group_id,),
            ).fetchone()
            return self.row_to_group(row)

    def get_group(self, group_id: int) -> Group | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM groups WHERE id = ?",
                (group_id,),
            ).fetchone()
            return self.row_to_group(row) if row else None

    def get_group_by_invite(self, invite_code: str) -> Group | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM groups WHERE invite_code = ?",
                (invite_code,),
            ).fetchone()
            return self.row_to_group(row) if row else None

    def list_public_groups(self) -> list[Group]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM groups WHERE is_public = 1 ORDER BY id",
            ).fetchall()
            return [self.row_to_group(r) for r in rows]

    def is_member(self, group_id: int, user_id: int) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT 1 FROM group_members
                WHERE group_id = ? AND user_id = ?
                """,
                (group_id, user_id),
            ).fetchone()
            return row is not None

    def add_member(self, group_id: int, user_id: int) -> None:
        if self.is_blocked(group_id, user_id):
            raise UserBlockedInGroupError("User is blocked in this group")
        with self._connect() as conn:
            if not conn.execute(
                "SELECT 1 FROM groups WHERE id = ?",
                (group_id,),
            ).fetchone():
                raise GroupNotFoundError("Group not found")
            conn.execute(
                """
                INSERT OR IGNORE INTO group_members (group_id, user_id, joined_at)
                VALUES (?, ?, ?)
                """,
                (group_id, user_id, utcnow().isoformat()),
            )

    def remove_member(self, group_id: int, user_id: int) -> None:
        with self._connect() as conn:
            conn.execute(
                "DELETE FROM group_members WHERE group_id = ? AND user_id = ?",
                (group_id, user_id),
            )

    def list_group_members(self, group_id: int) -> list[int]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT user_id FROM group_members
                WHERE group_id = ?
                ORDER BY user_id
                """,
                (group_id,),
            ).fetchall()
            return [r["user_id"] for r in rows]

    def is_blocked(self, group_id: int, user_id: int) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT 1 FROM group_blocks
                WHERE group_id = ? AND user_id = ?
                """,
                (group_id, user_id),
            ).fetchone()
            return row is not None

    def list_blocked_members(self, group_id: int) -> list[int]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT user_id FROM group_blocks
                WHERE group_id = ?
                ORDER BY user_id
                """,
                (group_id,),
            ).fetchall()
            return [r["user_id"] for r in rows]

    def block_member(self, group_id: int, user_id: int, admin_id: int) -> None:
        group = self.get_group(group_id)
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

        now = utcnow().isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO group_blocks (group_id, user_id, blocked_at, blocked_by_id)
                VALUES (?, ?, ?, ?)
                """,
                (group_id, user_id, now, admin_id),
            )
        self.remove_member(group_id, user_id)
        self.unsubscribe_wishes(group_id, user_id)
        member = self.get_user(user_id)
        if member and member.current_group_id == group_id:
            self.set_current_group(user_id, None)

    def unblock_member(self, group_id: int, user_id: int, admin_id: int) -> None:
        group = self.get_group(group_id)
        if not group:
            raise GroupNotFoundError("Group not found")
        if group.admin_id != admin_id:
            raise NotGroupAdminError("Not group admin")
        with self._connect() as conn:
            conn.execute(
                "DELETE FROM group_blocks WHERE group_id = ? AND user_id = ?",
                (group_id, user_id),
            )

    def set_group_public(self, group_id: int, admin_id: int, is_public: bool) -> Group:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM groups WHERE id = ?",
                (group_id,),
            ).fetchone()
            if not row:
                raise GroupNotFoundError("Group not found")
            if row["admin_id"] != admin_id:
                raise RepositoryError("Not group admin")

            conn.execute(
                "UPDATE groups SET is_public = ? WHERE id = ?",
                (int(is_public), group_id),
            )
            updated = conn.execute(
                "SELECT * FROM groups WHERE id = ?",
                (group_id,),
            ).fetchone()
            return self.row_to_group(updated)

    def create_wish(self, group_id: int, author_id: int, text: str) -> Wish:
        if not self.get_group(group_id):
            raise GroupNotFoundError("Group not found")
        if not self.is_member(group_id, author_id):
            raise UserNotMemberError("Not a group member")

        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO wishes (group_id, author_id, text, status)
                VALUES (?, ?, ?, ?)
                """,
                (group_id, author_id, text, WishStatus.OPEN),
            )
            row = conn.execute(
                "SELECT * FROM wishes WHERE id = ?",
                (cursor.lastrowid,),
            ).fetchone()
            return self.row_to_wish(row)

    def list_open_wishes(self, group_id: int) -> list[OpenWish]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, text FROM wishes
                WHERE group_id = ? AND status = ? AND {WISH_NOT_DELETED}
                ORDER BY id
                """.format(WISH_NOT_DELETED=WISH_NOT_DELETED),
                (group_id, WishStatus.OPEN),
            ).fetchall()
            return [OpenWish(id=r["id"], text=r["text"]) for r in rows]

    def get_wish(self, wish_id: int) -> Wish | None:
        with self._connect() as conn:
            row = conn.execute(
                f"SELECT * FROM wishes WHERE id = ? AND {WISH_NOT_DELETED}",
                (wish_id,),
            ).fetchone()
            return self.row_to_wish(row) if row else None

    def take_wish(self, wish_id: int, taker_id: int) -> Wish:
        with self._connect() as conn:
            row = conn.execute(
                f"SELECT * FROM wishes WHERE id = ? AND {WISH_NOT_DELETED}",
                (wish_id,),
            ).fetchone()
            if not row:
                raise WishNotFoundError("Wish not found")
            wish = self.row_to_wish(row)
            if wish.status != WishStatus.OPEN:
                raise WishAlreadyTakenError("Wish already taken")
            if wish.author_id == taker_id:
                raise CannotTakeOwnWishError("Cannot take own wish")
            if not self.is_member(wish.group_id, taker_id):
                raise UserNotMemberError("Not a group member")

            now = utcnow().isoformat()
            cursor = conn.execute(
                f"""
                UPDATE wishes
                SET status = ?, taken_by_id = ?, taken_at = ?
                WHERE id = ? AND status = ? AND {WISH_NOT_DELETED}
                """,
                (WishStatus.TAKEN, taker_id, now, wish_id, WishStatus.OPEN),
            )
            if cursor.rowcount == 0:
                raise WishAlreadyTakenError("Wish already taken")

            updated = conn.execute(
                "SELECT * FROM wishes WHERE id = ?",
                (wish_id,),
            ).fetchone()
            return self.row_to_wish(updated)

    def list_taken_by_user(self, user_id: int, group_id: int) -> list[Wish]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM wishes
                WHERE group_id = ? AND status = ? AND taken_by_id = ? AND {WISH_NOT_DELETED}
                ORDER BY id
                """.format(WISH_NOT_DELETED=WISH_NOT_DELETED),
                (group_id, WishStatus.TAKEN, user_id),
            ).fetchall()
            return [self.row_to_wish(r) for r in rows]

    def complete_wish(self, wish_id: int, taker_id: int, message: str) -> Wish:
        with self._connect() as conn:
            row = conn.execute(
                f"SELECT * FROM wishes WHERE id = ? AND {WISH_NOT_DELETED}",
                (wish_id,),
            ).fetchone()
            if not row:
                raise WishNotFoundError("Wish not found")
            wish = self.row_to_wish(row)
            if wish.taken_by_id != taker_id:
                raise NotWishTakerError("Not the wish taker")
            if wish.status != WishStatus.TAKEN:
                raise WishAlreadyTakenError("Wish is not in taken state")

            now = utcnow().isoformat()
            conn.execute(
                """
                UPDATE wishes
                SET status = ?, completed_at = ?, completion_message = ?
                WHERE id = ?
                """,
                (WishStatus.COMPLETED, now, message, wish_id),
            )
            updated = conn.execute(
                "SELECT * FROM wishes WHERE id = ?",
                (wish_id,),
            ).fetchone()
            return self.row_to_wish(updated)

    def list_wishes_by_author(self, author_id: int, group_id: int) -> list[Wish]:
        with self._connect() as conn:
            rows = conn.execute(
                f"""
                SELECT * FROM wishes
                WHERE group_id = ? AND author_id = ? AND {WISH_NOT_DELETED}
                ORDER BY id
                """,
                (group_id, author_id),
            ).fetchall()
            return [self.row_to_wish(r) for r in rows]

    def delete_wish(self, wish_id: int, author_id: int) -> Wish:
        with self._connect() as conn:
            row = conn.execute(
                f"SELECT * FROM wishes WHERE id = ? AND {WISH_NOT_DELETED}",
                (wish_id,),
            ).fetchone()
            if not row:
                raise WishNotFoundError("Wish not found")
            wish = self.row_to_wish(row)
            if wish.author_id != author_id:
                raise NotWishAuthorError("Not the wish author")

            conn.execute(
                "UPDATE wishes SET deleted = 1 WHERE id = ?",
                (wish_id,),
            )
            return wish

    def subscribe_wishes(self, group_id: int, user_id: int) -> None:
        if not self.get_group(group_id):
            raise GroupNotFoundError("Group not found")
        if not self.is_member(group_id, user_id):
            raise UserNotMemberError("Not a group member")
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO wish_subscriptions (group_id, user_id, subscribed_at)
                VALUES (?, ?, ?)
                """,
                (group_id, user_id, utcnow().isoformat()),
            )

    def unsubscribe_wishes(self, group_id: int, user_id: int) -> None:
        with self._connect() as conn:
            conn.execute(
                "DELETE FROM wish_subscriptions WHERE group_id = ? AND user_id = ?",
                (group_id, user_id),
            )

    def is_subscribed_wishes(self, group_id: int, user_id: int) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT 1 FROM wish_subscriptions
                WHERE group_id = ? AND user_id = ?
                """,
                (group_id, user_id),
            ).fetchone()
            return row is not None

    def list_wish_subscribers(self, group_id: int) -> list[int]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT user_id FROM wish_subscriptions
                WHERE group_id = ?
                ORDER BY user_id
                """,
                (group_id,),
            ).fetchall()
            return [r["user_id"] for r in rows]

    def list_completed_wishes_by_author(self, author_id: int, group_id: int) -> list[Wish]:
        with self._connect() as conn:
            rows = conn.execute(
                f"""
                SELECT * FROM wishes
                WHERE group_id = ? AND author_id = ? AND status = ?
                AND {WISH_NOT_DELETED}
                ORDER BY completed_at DESC, id DESC
                """,
                (group_id, author_id, WishStatus.COMPLETED),
            ).fetchall()
            return [self.row_to_wish(r) for r in rows]

    def list_completed_wishes_by_taker(self, taker_id: int, group_id: int) -> list[Wish]:
        with self._connect() as conn:
            rows = conn.execute(
                f"""
                SELECT * FROM wishes
                WHERE group_id = ? AND taken_by_id = ? AND status = ?
                AND {WISH_NOT_DELETED}
                ORDER BY completed_at DESC, id DESC
                """,
                (group_id, taker_id, WishStatus.COMPLETED),
            ).fetchall()
            return [self.row_to_wish(r) for r in rows]
