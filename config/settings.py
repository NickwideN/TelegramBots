"""Общие настройки репозитория: режим запуска, БД, webhook (для всех ботов)."""

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote_plus

from environs import Env

from bots.wish_bot.services.repository import Repository, StorageNotConfiguredError

_REPO_ROOT = Path(__file__).resolve().parents[1]
_DEFAULT_ENV = _REPO_ROOT / ".env"
_DEFAULT_SQLITE_PATH = _REPO_ROOT / "data" / "telegram_bots.db"

_repository: Repository | None = None


def _strip_database_url_prefix(url: str) -> str:
    cleaned = url.strip()
    for prefix in ("DATABASE_URL=", "database_url="):
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix) :].strip()
    return cleaned


def resolve_database_url(env: Env) -> str | None:
    """DATABASE_URL или CLOUD_SQL_CONNECTION_NAME + POSTGRES_*."""
    direct = env("DATABASE_URL", None)
    if direct:
        direct = _strip_database_url_prefix(direct)
        if direct:
            return direct

    instance = env("CLOUD_SQL_CONNECTION_NAME", None)
    user = env("POSTGRES_USER", None)
    password = env("POSTGRES_PASSWORD", None)
    if not instance or not user or not password:
        return None

    dbname = env("POSTGRES_DB", "wish_bot")
    return (
        f"postgresql://{quote_plus(user)}:{quote_plus(password)}"
        f"@/{dbname}?host=/cloudsql/{instance.strip()}"
    )


@dataclass
class StorageSettings:
    backend: str
    database_url: str | None
    sqlite_path: str


@dataclass
class WebhookSettings:
    base_url: str | None
    path: str
    secret: str | None
    host: str
    port: int


@dataclass
class AppSettings:
    bot_mode: str
    storage: StorageSettings
    webhook: WebhookSettings


def load_app_settings(path: str | None = None) -> AppSettings:
    env = Env()
    env_file = Path(path) if path else _DEFAULT_ENV
    if env_file.is_file():
        env.read_env(env_file, override=True)

    bot_mode = env("BOT_MODE", "polling").strip().lower()
    if bot_mode not in ("polling", "webhook"):
        raise ValueError(f"Invalid BOT_MODE={bot_mode!r}; use 'polling' or 'webhook'")

    backend = env("DB_BACKEND", "sqlite").strip().lower()
    if backend not in ("sqlite", "postgres"):
        raise ValueError(f"Invalid DB_BACKEND={backend!r}; use 'sqlite' or 'postgres'")

    sqlite_path = env("SQLITE_PATH", str(_DEFAULT_SQLITE_PATH))

    return AppSettings(
        bot_mode=bot_mode,
        storage=StorageSettings(
            backend=backend,
            database_url=resolve_database_url(env),
            sqlite_path=sqlite_path,
        ),
        webhook=WebhookSettings(
            base_url=env("WEBHOOK_URL", None),
            path=env("WEBHOOK_PATH", "/webhook"),
            secret=env("WEBHOOK_SECRET", None),
            host=env("WEBHOOK_HOST", "0.0.0.0"),
            port=env.int("PORT", 8080),
        ),
    )


def create_repository(settings: AppSettings | None = None) -> Repository:
    global _repository
    if _repository is not None:
        return _repository

    from bots.wish_bot.services.postgres_storage import PostgresStorage
    from bots.wish_bot.services.sqlite_storage import SqliteStorage

    app = settings or load_app_settings()
    backend = app.storage.backend

    if backend == "sqlite":
        _repository = SqliteStorage(app.storage.sqlite_path)
    elif backend == "postgres":
        if not app.storage.database_url:
            raise StorageNotConfiguredError(
                "Postgres requires DATABASE_URL or "
                "CLOUD_SQL_CONNECTION_NAME + POSTGRES_USER + POSTGRES_PASSWORD"
            )
        _repository = PostgresStorage(app.storage.database_url)
    else:
        raise StorageNotConfiguredError(f"Unknown DB_BACKEND: {backend}")

    return _repository
