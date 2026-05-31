from bots.wish_bot.services.repository import Repository


def get_repository() -> Repository:
    from config.settings import create_repository

    return create_repository()


__all__ = ["Repository", "get_repository"]
