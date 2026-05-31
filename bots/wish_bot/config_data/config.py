from dataclasses import dataclass
from pathlib import Path

from environs import Env

from config.settings import AppSettings, load_app_settings

_REPO_ROOT = Path(__file__).resolve().parents[3]
_DEFAULT_ENV = _REPO_ROOT / ".env"


@dataclass
class TgBot:
    token: str


@dataclass
class Config:
    tg_bot: TgBot
    app: AppSettings

    @property
    def bot_mode(self) -> str:
        return self.app.bot_mode

    @property
    def storage(self):
        return self.app.storage

    @property
    def webhook(self):
        return self.app.webhook


def load_config(path: str | None = None) -> Config:
    env = Env()
    env_file = Path(path) if path else _DEFAULT_ENV
    if env_file.is_file():
        env.read_env(env_file, override=True)

    return Config(
        tg_bot=TgBot(token=env.str("WISH_BOT_TOKEN", default="")),
        app=load_app_settings(path),
    )
