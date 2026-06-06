"""Персистентное FSM-хранилище aiogram / aiogram-dialog (SQLite и PostgreSQL)."""

from __future__ import annotations

import asyncio
import json
import sqlite3
from collections.abc import Mapping
from typing import Any

from aiogram.exceptions import DataNotDictLikeError
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.base import BaseStorage, StateType, StorageKey

from bots.wish_bot.services.postgres_connect import PostgresConnectionFactory

_STATE_BY_NAME: dict[str, State] = {}


def _storage_key_to_str(key: StorageKey) -> str:
    return json.dumps(
        {
            "bot_id": key.bot_id,
            "chat_id": key.chat_id,
            "user_id": key.user_id,
            "thread_id": key.thread_id,
            "business_connection_id": key.business_connection_id,
            "destiny": key.destiny,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def _state_to_str(state: StateType | None) -> str | None:
    if isinstance(state, State):
        return state.state
    return state


def _json_safe(value: Any) -> Any:
    if isinstance(value, State):
        return value.state
    if isinstance(value, Mapping):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def _dump_data(data: dict[str, Any]) -> str:
    return json.dumps(_json_safe(data), ensure_ascii=False)


def register_state_groups(*groups: type[StatesGroup]) -> None:
    for group in groups:
        for state in group.__all_states__:
            if state.state:
                _STATE_BY_NAME[state.state] = state


def resolve_state(value: StateType | None) -> StateType | None:
    if value is None or isinstance(value, State):
        return value
    if isinstance(value, str):
        return _STATE_BY_NAME.get(value, value)
    return value


class SqliteFsmStorage(BaseStorage):
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    async def close(self) -> None:
        return None

    async def set_state(self, key: StorageKey, state: StateType = None) -> None:
        await asyncio.to_thread(self._set_state_sync, key, state)

    def _set_state_sync(self, key: StorageKey, state: StateType = None) -> None:
        storage_key = _storage_key_to_str(key)
        state_value = _state_to_str(state)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO fsm_data (storage_key, state, data_json)
                VALUES (?, ?, '{}')
                ON CONFLICT(storage_key) DO UPDATE SET state = excluded.state
                """,
                (storage_key, state_value),
            )

    async def get_state(self, key: StorageKey) -> str | None:
        return await asyncio.to_thread(self._get_state_sync, key)

    def _get_state_sync(self, key: StorageKey) -> str | None:
        storage_key = _storage_key_to_str(key)
        with self._connect() as conn:
            row = conn.execute(
                "SELECT state FROM fsm_data WHERE storage_key = ?",
                (storage_key,),
            ).fetchone()
        return row["state"] if row else None

    async def set_data(self, key: StorageKey, data: Mapping[str, Any]) -> None:
        if not isinstance(data, dict):
            msg = f"Data must be a dict or dict-like object, got {type(data).__name__}"
            raise DataNotDictLikeError(msg)
        await asyncio.to_thread(self._set_data_sync, key, data.copy())

    def _set_data_sync(self, key: StorageKey, data: dict[str, Any]) -> None:
        storage_key = _storage_key_to_str(key)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO fsm_data (storage_key, state, data_json)
                VALUES (?, NULL, ?)
                ON CONFLICT(storage_key) DO UPDATE SET data_json = excluded.data_json
                """,
                (storage_key, _dump_data(data)),
            )

    async def get_data(self, key: StorageKey) -> dict[str, Any]:
        return await asyncio.to_thread(self._get_data_sync, key)

    def _get_data_sync(self, key: StorageKey) -> dict[str, Any]:
        storage_key = _storage_key_to_str(key)
        with self._connect() as conn:
            row = conn.execute(
                "SELECT data_json FROM fsm_data WHERE storage_key = ?",
                (storage_key,),
            ).fetchone()
        if not row:
            return {}
        return json.loads(row["data_json"])


class PostgresFsmStorage(BaseStorage):
    def __init__(self, database_url: str) -> None:
        if database_url.startswith("postgres://"):
            database_url = "postgresql://" + database_url[len("postgres://") :]
        self._factory = PostgresConnectionFactory(database_url)

    async def close(self) -> None:
        return None

    async def set_state(self, key: StorageKey, state: StateType = None) -> None:
        await asyncio.to_thread(self._set_state_sync, key, state)

    def _set_state_sync(self, key: StorageKey, state: StateType = None) -> None:
        storage_key = _storage_key_to_str(key)
        state_value = _state_to_str(state)
        conn = self._factory.connect()
        try:
            conn.execute(
                """
                INSERT INTO fsm_data (storage_key, state, data_json)
                VALUES (%s, %s, '{}'::jsonb)
                ON CONFLICT (storage_key) DO UPDATE SET state = EXCLUDED.state
                """,
                (storage_key, state_value),
            )
            conn.commit()
        finally:
            conn.close()

    async def get_state(self, key: StorageKey) -> str | None:
        return await asyncio.to_thread(self._get_state_sync, key)

    def _get_state_sync(self, key: StorageKey) -> str | None:
        storage_key = _storage_key_to_str(key)
        conn = self._factory.connect()
        try:
            row = conn.execute(
                "SELECT state FROM fsm_data WHERE storage_key = %s",
                (storage_key,),
            ).fetchone()
        finally:
            conn.close()
        return row["state"] if row else None

    async def set_data(self, key: StorageKey, data: Mapping[str, Any]) -> None:
        if not isinstance(data, dict):
            msg = f"Data must be a dict or dict-like object, got {type(data).__name__}"
            raise DataNotDictLikeError(msg)
        await asyncio.to_thread(self._set_data_sync, key, data.copy())

    def _set_data_sync(self, key: StorageKey, data: dict[str, Any]) -> None:
        storage_key = _storage_key_to_str(key)
        conn = self._factory.connect()
        try:
            conn.execute(
                """
                INSERT INTO fsm_data (storage_key, state, data_json)
                VALUES (%s, NULL, %s::jsonb)
                ON CONFLICT (storage_key) DO UPDATE SET data_json = EXCLUDED.data_json
                """,
                (storage_key, _dump_data(data)),
            )
            conn.commit()
        finally:
            conn.close()

    async def get_data(self, key: StorageKey) -> dict[str, Any]:
        return await asyncio.to_thread(self._get_data_sync, key)

    def _get_data_sync(self, key: StorageKey) -> dict[str, Any]:
        storage_key = _storage_key_to_str(key)
        conn = self._factory.connect()
        try:
            row = conn.execute(
                "SELECT data_json FROM fsm_data WHERE storage_key = %s",
                (storage_key,),
            ).fetchone()
        finally:
            conn.close()
        if not row:
            return {}
        data = row["data_json"]
        if isinstance(data, dict):
            return data
        return json.loads(data)
