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


async def main() -> None:
    tasks: list[asyncio.Task] = []

    if _is_enabled("WISH_BOT_ENABLED", "1"):
        from bots.wish_bot.main import run as run_wish_bot

        logger.info("Запуск wish_bot")
        tasks.append(asyncio.create_task(run_wish_bot(), name="wish_bot"))

    if not tasks:
        logger.error("Нет включённых ботов. Проверьте переменные *_BOT_ENABLED в .env")
        return

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
