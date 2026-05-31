"""Postgres (psycopg2): Cloud Run — сокет /cloudsql/…, иначе DATABASE_URL."""

import logging
from dataclasses import dataclass
from typing import Any
from urllib.parse import unquote, urlparse

import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

_SOCKET_PREFIX = "/cloudsql/"


@dataclass(frozen=True)
class _CloudSqlParams:
    connection_name: str
    user: str
    password: str
    database: str


class PgConnection:
    def __init__(self, conn: Any) -> None:
        self._conn = conn

    def execute(self, query: str, params: Any = None) -> Any:
        cur = self._conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(query, params)
        return cur

    def commit(self) -> None:
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()


def _parse_cloud_sql_url(database_url: str) -> _CloudSqlParams | None:
    if _SOCKET_PREFIX not in database_url:
        return None
    parsed = urlparse(database_url)
    connection_name = database_url.split(_SOCKET_PREFIX, 1)[1].split("?", 1)[0]
    user = unquote(parsed.username or "")
    password = unquote(parsed.password or "")
    database = (parsed.path or "/").lstrip("/") or "postgres"
    if not user or not connection_name:
        return None
    return _CloudSqlParams(connection_name, user, password, database)


class PostgresConnectionFactory:
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url
        self._cloud_sql = _parse_cloud_sql_url(database_url)

    def connect(self) -> PgConnection:
        if self._cloud_sql:
            logger.info(
                "postgres: %s%s",
                _SOCKET_PREFIX,
                self._cloud_sql.connection_name,
            )
            raw = psycopg2.connect(
                dbname=self._cloud_sql.database,
                user=self._cloud_sql.user,
                password=self._cloud_sql.password,
                host=f"{_SOCKET_PREFIX}{self._cloud_sql.connection_name}",
                connect_timeout=15,
            )
            return PgConnection(raw)

        raw = psycopg2.connect(self._database_url, connect_timeout=15)
        return PgConnection(raw)
