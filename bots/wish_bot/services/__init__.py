from pathlib import Path

from bots.wish_bot.config_data import Config, load_config
from bots.wish_bot.services.memory_storage import MemoryStorage
from bots.wish_bot.services.postgres_storage import PostgresStorage
from bots.wish_bot.services.repository import Repository, StorageNotConfiguredError
from bots.wish_bot.services.sqlite_storage import SqliteStorage

_storage: Repository | None = None

_DEFAULT_SQLITE_PATH = Path(__file__).parent.parent / "data" / "wish_bot.db"


def get_repository(config: Config | None = None) -> Repository:
    global _storage
    if _storage is not None:
        return _storage

    cfg = config or load_config()
    backend = cfg.storage.backend.lower()

    if backend == "memory":
        _storage = MemoryStorage()
    elif backend == "sqlite":
        db_path = cfg.storage.sqlite_path or str(_DEFAULT_SQLITE_PATH)
        _storage = SqliteStorage(db_path)
    elif backend == "postgres":
        if not cfg.storage.database_url:
            raise StorageNotConfiguredError("DATABASE_URL is required for postgres storage")
        _storage = PostgresStorage(cfg.storage.database_url)
    else:
        raise StorageNotConfiguredError(f"Unknown storage backend: {backend}")

    return _storage
