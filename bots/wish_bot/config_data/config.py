from dataclasses import dataclass

from environs import Env


@dataclass
class TgBot:
    token: str


@dataclass
class Storage:
    backend: str
    database_url: str | None
    sqlite_path: str | None


@dataclass
class Config:
    tg_bot: TgBot
    storage: Storage


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env("WISH_BOT_TOKEN"),
        ),
        storage=Storage(
            backend=env("WISH_BOT_STORAGE", "sqlite"),
            database_url=env("DATABASE_URL", None),
            sqlite_path=env("WISH_BOT_SQLITE_PATH", None),
        ),
    )
