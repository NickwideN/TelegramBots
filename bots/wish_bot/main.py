import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from bots.wish_bot import config_data
from bots.wish_bot.handlers import commands

logger = logging.getLogger(__name__)


async def run() -> None:
    config: config_data.Config = config_data.load_config()

    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(commands.router)

    logger.info("wish_bot: polling started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[{asctime}] #{levelname:8} {filename}:{lineno} - {name} - {message}",
        style="{",
    )
    asyncio.run(run())
