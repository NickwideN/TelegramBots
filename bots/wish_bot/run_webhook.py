import asyncio
import logging

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from bots.wish_bot.bootstrap import (
    build_webhook_url,
    initialize_bot_identity,
    normalize_webhook_path,
    setup_bot_app,
)
from bots.wish_bot.config_data import Config, load_config
from config.settings import create_repository

logger = logging.getLogger(__name__)


async def health_handler(_request: web.Request) -> web.Response:
    return web.Response(text="ok")


def _log_startup_config(config: Config) -> None:
    token = config.tg_bot.token or ""
    masked = f"{token[:8]}…" if len(token) > 8 else "(empty)"
    logger.info(
        "config: BOT_MODE=%s DB_BACKEND=%s PORT=%s WEBHOOK_URL=%s token=%s",
        config.bot_mode,
        config.storage.backend,
        config.webhook.port,
        config.webhook.base_url or "(not set)",
        masked,
    )


def _validate_webhook_config(config: Config) -> None:
    if config.bot_mode != "webhook":
        raise RuntimeError(
            f"BOT_MODE={config.bot_mode!r}, expected 'webhook'. "
            "Use bots.wish_bot.run_polling for polling mode."
        )
    if not config.tg_bot.token:
        raise RuntimeError(
            "WISH_BOT_TOKEN is not set. Add it in Cloud Run → Variables and secrets."
        )
    if config.storage.backend == "postgres" and not config.storage.database_url:
        raise RuntimeError("DATABASE_URL is required when DB_BACKEND=postgres.")
    if not config.webhook.base_url:
        logger.warning(
            "WEBHOOK_URL is not set — HTTP server will start, but Telegram updates "
            "will not arrive until you set WEBHOOK_URL to your Cloud Run URL and redeploy."
        )


def _build_app(config: Config) -> tuple[web.Application, Bot, Dispatcher, str | None]:
    bot, dp, _translator_hub = setup_bot_app(config)
    webhook_path = normalize_webhook_path(config.webhook.path)
    webhook_url = (
        build_webhook_url(config.webhook.base_url, config.webhook.path)
        if config.webhook.base_url
        else None
    )

    app = web.Application()
    app.router.add_get("/health", health_handler)

    webhook_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=config.webhook.secret,
    )
    webhook_handler.register(app, path=webhook_path)
    setup_application(app, dp, bot=bot)

    return app, bot, dp, webhook_url


async def _serve(config: Config) -> None:
    app, bot, dp, webhook_url = _build_app(config)
    host = config.webhook.host
    port = config.webhook.port

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=host, port=port)
    await site.start()
    logger.info("wish_bot: HTTP listening on %s:%s", host, port)

    try:
        create_repository(config.app)
        logger.info("wish_bot: database ready (%s)", config.storage.backend)

        await initialize_bot_identity(bot)

        if webhook_url:
            await bot.set_webhook(
                webhook_url,
                secret_token=config.webhook.secret,
                drop_pending_updates=True,
            )
            logger.info("wish_bot: webhook set to %s", webhook_url)
    except Exception:
        logger.exception("wish_bot: init after HTTP listen failed")
        await runner.cleanup()
        raise

    try:
        await asyncio.Event().wait()
    finally:
        await bot.session.close()
        await runner.cleanup()


def main() -> None:
    try:
        config = load_config()
        _log_startup_config(config)
        _validate_webhook_config(config)
        asyncio.run(_serve(config))
    except Exception:
        logger.exception("wish_bot: startup failed")
        raise SystemExit(1) from None
