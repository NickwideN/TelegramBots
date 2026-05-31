"""Подключение к Cloud SQL (официальный Connector — надёжнее сокета на Cloud Run)."""

import logging
from dataclasses import dataclass
from urllib.parse import unquote, urlparse

import psycopg
from psycopg.rows import dict_row

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CloudSqlTarget:
    connection_name: str
    user: str
    password: str
    database: str


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
                "postgres: Cloud SQL Connector → %s (db=%s, user=%s)",
                self._cloud_sql.connection_name,
                self._cloud_sql.database,
                self._cloud_sql.user,
            )
        else:
            logger.info("postgres: direct psycopg connection")

    def connect(self) -> psycopg.Connection:
        if self._cloud_sql and self._connector:
            conn = self._connector.connect(
                self._cloud_sql.connection_name,
                "psycopg",
                user=self._cloud_sql.user,
                password=self._cloud_sql.password,
                db=self._cloud_sql.database,
            )
            conn.row_factory = dict_row
            return conn

        return psycopg.connect(
            self._database_url,
            connect_timeout=15,
            row_factory=dict_row,
        )
