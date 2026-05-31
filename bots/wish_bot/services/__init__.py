from config.settings import create_repository, load_app_settings

from bots.wish_bot.services.repository import Repository

__all__ = ["Repository", "create_repository", "get_repository", "load_app_settings"]


def get_repository() -> Repository:
    return create_repository()
