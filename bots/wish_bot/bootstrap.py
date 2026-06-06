import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram_dialog import setup_dialogs
from fluentogram import TranslatorHub

from bots.wish_bot.config_data import Config
from bots.wish_bot.dialogs import menu_dialog
from bots.wish_bot.handlers import commands, dev, fallback, groups, inline_share, moderation, wishes
from bots.wish_bot.middlewares.create_group_flow import CreateGroupVisibilityMiddleware
from bots.wish_bot.middlewares.group_context import GroupContextMiddleware
from bots.wish_bot.middlewares.i18n import TranslatorRunnerMiddleware
from bots.wish_bot.utils.bot_info import set_bot_username
from bots.wish_bot.utils.i18n import create_translator_hub

logger = logging.getLogger(__name__)


def setup_bot_app(config: Config) -> tuple[Bot, Dispatcher, TranslatorHub]:
    """Bot + Dispatcher без подключения к БД."""
    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode="HTML"),
    )

    translator_hub = create_translator_hub()
    dp = Dispatcher(storage=MemoryStorage())
    dp.workflow_data["_translator_hub"] = translator_hub
    dp.workflow_data["tester_ids"] = config.tester_ids

    dp.update.middleware(GroupContextMiddleware())
    dp.update.middleware(TranslatorRunnerMiddleware())
    dp.update.middleware(CreateGroupVisibilityMiddleware())

    dp.include_router(commands.router)
    dp.include_router(dev.router)
    dp.include_router(groups.router)
    dp.include_router(moderation.router)
    dp.include_router(wishes.router)
    dp.include_router(inline_share.router)
    dp.include_router(menu_dialog)
    dp.include_router(fallback.router)

    setup_dialogs(dp)

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
