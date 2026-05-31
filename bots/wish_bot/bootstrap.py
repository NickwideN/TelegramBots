import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage
from fluentogram import TranslatorHub

from bots.wish_bot.config_data import Config
from bots.wish_bot.handlers import commands, groups, moderation, subscriptions, wishes
from bots.wish_bot.middlewares.group_context import GroupContextMiddleware
from bots.wish_bot.middlewares.i18n import TranslatorRunnerMiddleware
from bots.wish_bot.services import get_repository
from bots.wish_bot.utils.bot_info import set_bot_username
from bots.wish_bot.utils.i18n import create_translator_hub

logger = logging.getLogger(__name__)


def create_fsm_storage(_config: Config) -> BaseStorage:
    return MemoryStorage()


def setup_bot_app(config: Config) -> tuple[Bot, Dispatcher, TranslatorHub]:
    """Сборка бота без сетевых вызовов (удобно до старта HTTP на Cloud Run)."""
    repo = get_repository(config)
    backend = config.storage.backend.lower()
    if backend == "sqlite":
        path = config.storage.sqlite_path
        if path is None and hasattr(repo, "db_path"):
            path = str(repo.db_path)
        logger.info("wish_bot storage: sqlite (%s)", path)
    else:
        logger.info("wish_bot storage: %s", backend)

    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode="HTML"),
    )

    translator_hub = create_translator_hub()
    dp = Dispatcher(storage=create_fsm_storage(config))
    dp.workflow_data["_translator_hub"] = translator_hub

    dp.update.middleware(GroupContextMiddleware())
    dp.update.middleware(TranslatorRunnerMiddleware())

    dp.include_router(commands.router)
    dp.include_router(groups.router)
    dp.include_router(moderation.router)
    dp.include_router(subscriptions.router)
    dp.include_router(wishes.router)

    return bot, dp, translator_hub


async def initialize_bot_identity(bot: Bot) -> None:
    me = await bot.get_me()
    if me.username:
        set_bot_username(me.username)
    logger.info("wish_bot: bot @%s (id=%s)", me.username, me.id)


def normalize_webhook_path(path: str) -> str:
    path = path.strip()
    if not path.startswith("/"):
        path = f"/{path}"
    return path


def build_webhook_url(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}{normalize_webhook_path(path)}"


# Обратная совместимость
async def setup_bot(config: Config) -> tuple[Bot, Dispatcher, TranslatorHub]:
    bot, dp, hub = setup_bot_app(config)
    await initialize_bot_identity(bot)
    return bot, dp, hub
