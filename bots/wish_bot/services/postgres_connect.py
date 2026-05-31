"""Postgres через psycopg2. На Cloud Run — Unix-сокет /cloudsql/… (без Python Connector)."""

import logging
from dataclasses import dataclass
from typing import Any
from urllib.parse import unquote, urlparse

import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

CLOUDSQL_SOCKET_PREFIX = "/cloudsql/"


@dataclass(frozen=True)
class CloudSqlTarget:
    connection_name: str
    user: str
    password: str
    database: str


class PgConnection:
    """Обёртка с API conn.execute() — как в psycopg3, на базе psycopg2."""

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


def parse_cloud_sql_target(database_url: str) -> CloudSqlTarget | None:
    if CLOUDSQL_SOCKET_PREFIX not in database_url:
        return None
    parsed = urlparse(database_url)
    connection_name = database_url.split(CLOUDSQL_SOCKET_PREFIX, 1)[1].split("?", 1)[0]
    user = unquote(parsed.username or "")
    password = unquote(parsed.password or "")
    database = (parsed.path or "/").lstrip("/") or "postgres"
    if not user or not connection_name:
        return None
    return CloudSqlTarget(connection_name, user, password, database)


class PostgresConnectionFactory:
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url
        self._cloud_sql = parse_cloud_sql_target(database_url)

        if self._cloud_sql:
            logger.info(
                "postgres: Cloud Run socket %s%s (db=%s, user=%s)",
                CLOUDSQL_SOCKET_PREFIX,
                self._cloud_sql.connection_name,
                self._cloud_sql.database,
                self._cloud_sql.user,
            )
        else:
            logger.info("postgres: direct connection (DATABASE_URL)")

    def connect(self) -> PgConnection:
        if self._cloud_sql:
            raw = psycopg2.connect(
                dbname=self._cloud_sql.database,
                user=self._cloud_sql.user,
                password=self._cloud_sql.password,
                host=f"{CLOUDSQL_SOCKET_PREFIX}{self._cloud_sql.connection_name}",
                connect_timeout=15,
            )
            return PgConnection(raw)

        raw = psycopg2.connect(self._database_url, connect_timeout=15)
        return PgConnection(raw)
