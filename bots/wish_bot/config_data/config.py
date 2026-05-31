from dataclasses import dataclass
from pathlib import Path

from environs import Env

_REPO_ROOT = Path(__file__).resolve().parents[3]
_DEFAULT_ENV = _REPO_ROOT / ".env"


@dataclass
class TgBot:
    token: str


@dataclass
class Storage:
    backend: str
    database_url: str | None
    sqlite_path: str | None


@dataclass
class WebhookSettings:
    base_url: str | None
    path: str
    secret: str | None
    host: str
    port: int


@dataclass
class Config:
    tg_bot: TgBot
    storage: Storage
    bot_mode: str
    webhook: WebhookSettings


def load_config(path: str | None = None) -> Config:
    env = Env()
    env_file = Path(path) if path else _DEFAULT_ENV
    if env_file.is_file():
        env.read_env(env_file, override=True)

    bot_mode = env("BOT_MODE", "polling").strip().lower()
    if bot_mode not in ("polling", "webhook"):
        raise ValueError(f"Invalid BOT_MODE={bot_mode!r}; use 'polling' or 'webhook'")

    return Config(
        tg_bot=TgBot(
            token=env.str("WISH_BOT_TOKEN", default=""),
        ),
        storage=Storage(
            backend=env("WISH_BOT_STORAGE", "sqlite"),
            database_url=env("DATABASE_URL", None),
            sqlite_path=env("WISH_BOT_SQLITE_PATH", None),
        ),
        bot_mode=bot_mode,
        webhook=WebhookSettings(
            base_url=env("WEBHOOK_URL", None),
            path=env("WEBHOOK_PATH", "/webhook"),
            secret=env("WEBHOOK_SECRET", None),
            host=env("WEBHOOK_HOST", "0.0.0.0"),
            port=env.int("PORT", 8080),
        ),
    )
