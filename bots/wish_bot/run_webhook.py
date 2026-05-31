import asyncio
import logging

from aiohttp import web
from aiogram import Bot
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from bots.wish_bot.bootstrap import (
    build_webhook_url,
    normalize_webhook_path,
    setup_bot,
)
from bots.wish_bot.config_data import Config, load_config

logger = logging.getLogger(__name__)


async def health_handler(_request: web.Request) -> web.Response:
    return web.Response(text="ok")


def _validate_webhook_config(config: Config) -> None:
    if config.bot_mode != "webhook":
        raise RuntimeError(
            f"BOT_MODE={config.bot_mode!r}, expected 'webhook'. "
            "Use bots.wish_bot.run_polling for polling mode."
        )
    if not config.webhook.base_url:
        raise RuntimeError("WEBHOOK_URL is required when BOT_MODE=webhook")
    if not config.tg_bot.token:
        raise RuntimeError("WISH_BOT_TOKEN is required")


async def _build_app(config: Config) -> web.Application:
    bot, dp, _translator_hub = await setup_bot(config)
    webhook_url = build_webhook_url(config.webhook.base_url, config.webhook.path)
    webhook_path = normalize_webhook_path(config.webhook.path)

    async def on_startup(bot: Bot) -> None:
        await bot.set_webhook(
            webhook_url,
            secret_token=config.webhook.secret,
            drop_pending_updates=True,
        )
        logger.info("wish_bot: webhook set to %s", webhook_url)

    dp.startup.register(on_startup)

    app = web.Application()
    app.router.add_get("/health", health_handler)

    webhook_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=config.webhook.secret,
    )
    webhook_handler.register(app, path=webhook_path)
    setup_application(app, dp, bot=bot)

    return app


def main() -> None:
    """Синхронная точка входа: свой event loop, без вложенного asyncio.run."""
    config = load_config()
    _validate_webhook_config(config)

    app = asyncio.run(_build_app(config))
    logger.info(
        "wish_bot: webhook server on %s:%s (path %s)",
        config.webhook.host,
        config.webhook.port,
        normalize_webhook_path(config.webhook.path),
    )
    web.run_app(app, host=config.webhook.host, port=config.webhook.port)


async def run() -> None:
    """Async entry for tests; production uses blocking main()."""
    config = load_config()
    _validate_webhook_config(config)
    app = await _build_app(config)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, config.webhook.host, config.webhook.port)
    await site.start()
    logger.info("wish_bot: webhook server started")
    try:
        await asyncio.Event().wait()
    finally:
        await runner.cleanup()
