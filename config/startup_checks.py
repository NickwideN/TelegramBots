"""Диагностика конфигурации при старте — смотреть в логах Cloud Run."""

import logging
import os
import re
from pathlib import Path

import psycopg2

from bots.wish_bot.bootstrap import build_webhook_url, normalize_webhook_path
from bots.wish_bot.config_data.config import Config
from bots.wish_bot.services.postgres_connect import (
    SOCKET_PREFIX,
    PostgresConnectionFactory,
    parse_cloud_sql_params,
)

logger = logging.getLogger(__name__)

_CONNECTION_NAME_RE = re.compile(r"^[^:]+:[^:]+:[^:]+$")
_SECRET_ENV_SUFFIXES = ("PASSWORD", "SECRET", "TOKEN")


def _env_status(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        return "MISSING"
    if any(part in name for part in _SECRET_ENV_SUFFIXES):
        return f"SET (len={len(value)})"
    if len(value) > 100:
        return f"SET ({value[:97]}…)"
    return f"SET ({value})"


def _log_cloud_sql_mount(connection_name: str) -> None:
    socket_root = Path(SOCKET_PREFIX)
    expected = socket_root / connection_name

    if not socket_root.is_dir():
        logger.error(
            "CHECK FAIL: каталог %s не найден — Cloud SQL не смонтирован. "
            "Cloud Run → Edit → Connections → добавьте инстанс %s",
            socket_root,
            connection_name,
        )
        return

    mounted = sorted(entry.name for entry in socket_root.iterdir())
    logger.info("CHECK INFO: смонтировано в %s: %s", socket_root, mounted or "(пусто)")

    if expected.is_dir():
        logger.info("CHECK OK: сокет Cloud SQL найден: %s", expected)
        return

    logger.error(
        "CHECK FAIL: ожидался сокет %s, но его нет среди %s. "
        "CLOUD_SQL_CONNECTION_NAME должен совпадать с Connections в Cloud Run",
        expected,
        mounted,
    )


def log_startup_diagnostics(config: Config) -> None:
    logger.info("=== startup diagnostics ===")
    logger.info(
        "runtime: K_SERVICE=%s K_REVISION=%s",
        os.getenv("K_SERVICE", "-"),
        os.getenv("K_REVISION", "-"),
    )
    logger.info("BOT_MODE=%s DB_BACKEND=%s", config.bot_mode, config.storage.backend)
    logger.info("WISH_BOT_ENABLED=%s", _env_status("WISH_BOT_ENABLED"))
    logger.info("WISH_BOT_TOKEN=%s", _env_status("WISH_BOT_TOKEN"))

    if config.storage.backend == "postgres":
        _log_postgres_env(config)
    elif config.storage.backend == "sqlite":
        logger.info("sqlite path=%s", config.storage.sqlite_path)

    if config.bot_mode == "webhook":
        _log_webhook_env(config)

    logger.info("=== end diagnostics ===")


def _log_postgres_env(config: Config) -> None:
    logger.info("--- postgres ---")
    has_direct_url = bool(os.getenv("DATABASE_URL", "").strip())
    logger.info("DATABASE_URL=%s", _env_status("DATABASE_URL"))
    logger.info("CLOUD_SQL_CONNECTION_NAME=%s", _env_status("CLOUD_SQL_CONNECTION_NAME"))
    logger.info("POSTGRES_USER=%s", _env_status("POSTGRES_USER"))
    logger.info("POSTGRES_PASSWORD=%s", _env_status("POSTGRES_PASSWORD"))
    logger.info("POSTGRES_DB=%s", _env_status("POSTGRES_DB"))

    database_url = config.storage.database_url
    if not database_url:
        logger.error(
            "CHECK FAIL: строка подключения не собрана. "
            "Нужен DATABASE_URL или CLOUD_SQL_CONNECTION_NAME + POSTGRES_USER + POSTGRES_PASSWORD",
        )
        return

    if has_direct_url:
        logger.info("CHECK OK: используется DATABASE_URL из окружения")
    else:
        logger.info("CHECK OK: DATABASE_URL собран из CLOUD_SQL_CONNECTION_NAME + POSTGRES_*")

    cloud = parse_cloud_sql_params(database_url)
    if cloud:
        logger.info(
            "target: connection_name=%s database=%s user=%s",
            cloud.connection_name,
            cloud.database,
            cloud.user,
        )
        if not _CONNECTION_NAME_RE.match(cloud.connection_name):
            logger.warning(
                "CHECK WARN: CLOUD_SQL_CONNECTION_NAME должен быть project:region:instance, "
                "сейчас %r",
                cloud.connection_name,
            )
        _log_cloud_sql_mount(cloud.connection_name)
    else:
        logger.info("target: прямое подключение (не Cloud SQL socket)")


def _log_webhook_env(config: Config) -> None:
    logger.info("--- webhook ---")
    logger.info("WEBHOOK_URL=%s", _env_status("WEBHOOK_URL"))
    logger.info("WEBHOOK_PATH=%s", _env_status("WEBHOOK_PATH"))
    logger.info("WEBHOOK_SECRET=%s", _env_status("WEBHOOK_SECRET"))
    logger.info("WEBHOOK_HOST=%s PORT=%s", config.webhook.host, config.webhook.port)

    if config.webhook.base_url:
        webhook_url = build_webhook_url(
            config.webhook.base_url,
            normalize_webhook_path(config.webhook.path),
        )
        logger.info("CHECK OK: webhook URL → %s", webhook_url)
    else:
        logger.error("CHECK FAIL: WEBHOOK_URL не задан — Telegram не будет слать апдейты")


def verify_postgres_connection(database_url: str) -> None:
    """Пробное подключение; при ошибке — подсказки в лог перед пробросом исключения."""
    factory = PostgresConnectionFactory(database_url)
    cloud = parse_cloud_sql_params(database_url)

    try:
        conn = factory.connect()
        conn.close()
        logger.info("CHECK OK: подключение к Postgres успешно")
    except psycopg2.OperationalError as exc:
        logger.error("CHECK FAIL: Postgres OperationalError: %s", exc)
        if cloud:
            logger.error(
                "Подсказки: 1) Cloud Run → Connections → %s "
                "2) service account → роль Cloud SQL Client "
                "3) инстанс Cloud SQL запущен "
                "4) база %r существует "
                "5) POSTGRES_USER/POSTGRES_PASSWORD верны",
                cloud.connection_name,
                cloud.database,
            )
            _log_cloud_sql_mount(cloud.connection_name)
        raise
