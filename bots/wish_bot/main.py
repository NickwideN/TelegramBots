import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from bots.wish_bot import config_data
from bots.wish_bot.handlers import commands, groups, moderation, subscriptions, wishes
from bots.wish_bot.middlewares.group_context import GroupContextMiddleware
from bots.wish_bot.middlewares.i18n import TranslatorRunnerMiddleware
from bots.wish_bot.services import get_repository
from bots.wish_bot.utils.bot_info import set_bot_username
from bots.wish_bot.utils.i18n import create_translator_hub

logger = logging.getLogger(__name__)


async def run() -> None:
    config: config_data.Config = config_data.load_config()
    get_repository(config)

    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    me = await bot.get_me()
    if me.username:
        set_bot_username(me.username)

    dp = Dispatcher(storage=MemoryStorage())
    translator_hub = create_translator_hub()

    dp.update.middleware(GroupContextMiddleware())
    dp.update.middleware(TranslatorRunnerMiddleware())

    dp.include_router(commands.router)
    dp.include_router(groups.router)
    dp.include_router(moderation.router)
    dp.include_router(subscriptions.router)
    dp.include_router(wishes.router)

    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("wish_bot: polling started")
    await dp.start_polling(bot, _translator_hub=translator_hub)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[{asctime}] #{levelname:8} {filename}:{lineno} - {name} - {message}",
        style="{",
    )
    asyncio.run(run())
