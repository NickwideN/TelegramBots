from aiogram import Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode
from fluentogram import TranslatorRunner

from bots.wish_bot.services import get_repository
from bots.wish_bot.services.repository import Group, User
from bots.wish_bot.states.menu import MenuSG
from bots.wish_bot.utils.send import answer_with_retry

router = Router()


async def start_menu(
    dialog_manager: DialogManager,
    current_group: Group | None,
) -> None:
    state = MenuSG.group if current_group else MenuSG.no_group
    await dialog_manager.start(state=state, mode=StartMode.RESET_STACK)


@router.message(CommandStart())
async def cmd_start(
    message: Message,
    command: CommandObject,
    dialog_manager: DialogManager,
    i18n: TranslatorRunner,
    user: User,
) -> None:
    """Приветственный экран."""
    args = (command.args or "").strip()

    if args.startswith("join_"):
        invite_code = args[5:]
        if invite_code:
            repo = get_repository()
            group = repo.get_group_by_invite(invite_code)
            if not group:
                await dialog_manager.start(
                    state=MenuSG.welcome_invite_invalid,
                    mode=StartMode.RESET_STACK,
                )
                return

            if repo.is_blocked(group.id, user.telegram_id):
                await answer_with_retry(
                    message,
                    i18n.get("message-blocked-in-group", name=group.name),
                )
                await dialog_manager.start(
                    state=MenuSG.welcome_invite_invalid,
                    mode=StartMode.RESET_STACK,
                )
                return

            if not repo.is_member(group.id, user.telegram_id):
                repo.add_member(group.id, user.telegram_id)
            repo.set_current_group(user.telegram_id, group.id)

            await dialog_manager.start(
                state=MenuSG.welcome_invite,
                mode=StartMode.RESET_STACK,
                data={"invite_code": invite_code, "group_name": group.name},
            )
            return

    await dialog_manager.start(state=MenuSG.welcome, mode=StartMode.RESET_STACK)


@router.message(Command(commands=["menu"]))
async def cmd_menu(
    message: Message,
    current_group: Group | None,
    dialog_manager: DialogManager,
) -> None:
    """Главное меню."""
    await start_menu(dialog_manager, current_group)


@router.message(Command(commands=["help"]))
async def cmd_help(message: Message, i18n: TranslatorRunner) -> None:
    """Обработчик команды /help."""
    from bots.wish_bot.utils.send import answer_with_retry

    await answer_with_retry(message, i18n.get("help-text"))
