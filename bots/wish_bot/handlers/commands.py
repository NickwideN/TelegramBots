from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Привет! Я <b>Бот желаний</b>.\n\n"
        "Здесь будет логика желаний — пока это заготовка проекта.",
    )
