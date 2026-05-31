import asyncio
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format="[{asctime}] #{levelname:8} {filename}:{lineno} - {name} - {message}",
    style="{",
)

logger = logging.getLogger(__name__)


def _is_enabled(name: str, default: str = "0") -> bool:
    return os.getenv(name, default).lower() in ("1", "true", "yes", "on")


def _bot_mode() -> str:
    return os.getenv("BOT_MODE", "polling").strip().lower()


async def main() -> None:
    if not _is_enabled("WISH_BOT_ENABLED", "1"):
        logger.error("Нет включённых ботов. Проверьте переменные *_BOT_ENABLED в .env")
        return

    mode = _bot_mode()
    logger.info("Запуск wish_bot (BOT_MODE=%s)", mode)

    if mode == "webhook":
        from bots.wish_bot.run_webhook import main as run_wish_webhook

        run_wish_webhook()
        return

    if mode == "polling":
        from bots.wish_bot.run_polling import run as run_wish_bot

        await run_wish_bot()
        return

    logger.error("Неизвестный BOT_MODE=%r. Используйте polling или webhook.", mode)


if __name__ == "__main__":
    asyncio.run(main())
