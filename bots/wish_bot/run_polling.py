import logging

from bots.wish_bot.bootstrap import initialize_bot_identity, setup_bot_app
from bots.wish_bot.config_data import load_config

logger = logging.getLogger(__name__)


async def run() -> None:
    config = load_config()
    if config.bot_mode != "polling":
        raise RuntimeError(
            f"BOT_MODE={config.bot_mode!r}, expected 'polling'. "
            "Use bots.wish_bot.run_webhook for webhook mode."
        )

    bot, dp, _translator_hub = setup_bot_app(config)
    await initialize_bot_identity(bot)

    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("wish_bot: polling started")
    await dp.start_polling(bot)
