"""Подключение к Cloud SQL (Connector) и обычный Postgres через psycopg2."""

import logging
from dataclasses import dataclass
from typing import Any
from urllib.parse import unquote, urlparse

import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


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
    if "/cloudsql/" not in database_url:
        return None
    parsed = urlparse(database_url)
    connection_name = database_url.split("/cloudsql/", 1)[1].split("?", 1)[0]
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
        self._connector = None

        if self._cloud_sql:
            from google.cloud.sql.connector import Connector

            self._connector = Connector()
            logger.info(
                "postgres: Cloud SQL Connector (psycopg2) → %s (db=%s, user=%s)",
                self._cloud_sql.connection_name,
                self._cloud_sql.database,
                self._cloud_sql.user,
            )
        else:
            logger.info("postgres: direct psycopg2 connection")

    def connect(self) -> PgConnection:
        if self._cloud_sql and self._connector:
            raw = self._connector.connect(
                self._cloud_sql.connection_name,
                "psycopg2",
                user=self._cloud_sql.user,
                password=self._cloud_sql.password,
                db=self._cloud_sql.database,
            )
            return PgConnection(raw)

        raw = psycopg2.connect(self._database_url, connect_timeout=15)
        return PgConnection(raw)
