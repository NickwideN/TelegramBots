import asyncio
import logging
import os

from config.settings import load_app_settings

logging.basicConfig(
    level=logging.INFO,
    format="[{asctime}] #{levelname:8} {filename}:{lineno} - {name} - {message}",
    style="{",
)

logger = logging.getLogger(__name__)


def _is_enabled(name: str, default: str = "0") -> bool:
    return os.getenv(name, default).lower() in ("1", "true", "yes", "on")


async def _run_polling() -> None:
    from bots.wish_bot.run_polling import run as run_wish_bot

    logger.info("Запуск wish_bot (BOT_MODE=polling)")
    await run_wish_bot()


if __name__ == "__main__":
    if not _is_enabled("WISH_BOT_ENABLED", "1"):
        logger.error("Нет включённых ботов. Проверьте переменные *_BOT_ENABLED в .env")
        raise SystemExit(1)

    mode = load_app_settings().bot_mode
    if mode == "webhook":
        from bots.wish_bot.run_webhook import main as run_wish_webhook

        logger.info("Запуск wish_bot (BOT_MODE=webhook)")
        run_wish_webhook()
    elif mode == "polling":
        asyncio.run(_run_polling())
    else:
        logger.error("Неизвестный BOT_MODE=%r. Используйте polling или webhook.", mode)
        raise SystemExit(1)
