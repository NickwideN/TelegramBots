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
    if mode != "polling":
        logger.error(
            "BOT_MODE=%r: для webhook запускайте run.py напрямую (ветка в __main__), "
            "не asyncio.run(main())",
            mode,
        )
        return

    logger.info("Запуск wish_bot (BOT_MODE=polling)")
    from bots.wish_bot.run_polling import run as run_wish_bot

    await run_wish_bot()


def _run_webhook() -> None:
    from bots.wish_bot.run_webhook import main as run_wish_webhook

    logger.info("Запуск wish_bot (BOT_MODE=webhook)")
    run_wish_webhook()


if __name__ == "__main__":
    if not _is_enabled("WISH_BOT_ENABLED", "1"):
        logger.error("Нет включённых ботов. Проверьте переменные *_BOT_ENABLED в .env")
        raise SystemExit(1)

    mode = _bot_mode()
    if mode == "webhook":
        _run_webhook()
    elif mode == "polling":
        asyncio.run(main())
    else:
        logger.error("Неизвестный BOT_MODE=%r. Используйте polling или webhook.", mode)
        raise SystemExit(1)
