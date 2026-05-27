from pathlib import Path

from fluent_compiler.bundle import FluentBundle
from fluentogram import FluentTranslator, TranslatorHub


def create_translator_hub() -> TranslatorHub:
    bot_dir = Path(__file__).parent.parent
    ru_path = str(bot_dir / "locales" / "ru" / "LC_MESSAGES" / "txt.ftl")
    en_path = str(bot_dir / "locales" / "en" / "LC_MESSAGES" / "txt.ftl")

    return TranslatorHub(
        {
            "ru": ("ru", "en"),
            "en": ("en", "ru"),
        },
        [
            FluentTranslator(
                locale="ru",
                translator=FluentBundle.from_files(
                    locale="ru-RU",
                    filenames=[ru_path],
                ),
            ),
            FluentTranslator(
                locale="en",
                translator=FluentBundle.from_files(
                    locale="en-US",
                    filenames=[en_path],
                ),
            ),
        ],
    )
