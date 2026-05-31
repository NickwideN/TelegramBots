import asyncio
import logging

from bots.wish_bot.run_polling import run

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[{asctime}] #{levelname:8} {filename}:{lineno} - {name} - {message}",
        style="{",
    )
    asyncio.run(run())
