from aiogram import Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode
from fluentogram import TranslatorRunner

from bots.wish_bot.services import get_repository
from bots.wish_bot.services.repository import Group
from bots.wish_bot.states.menu import MenuSG
from bots.wish_bot.utils.send import answer_with_retry

router = Router()


async def start_menu(
    dialog_manager: DialogManager,
    current_group: Group | None,
) -> None:
    state = MenuSG.group if current_group else MenuSG.no_group
    await dialog_manager.start(state=state, mode=StartMode.RESET_STACK)


async def _join_group_by_code(
    message: Message,
    invite_code: str,
    i18n: TranslatorRunner,
    user_id: int,
    dialog_manager: DialogManager,
) -> bool:
    repo = get_repository()
    group = repo.get_group_by_invite(invite_code)
    if not group:
        await answer_with_retry(message, i18n.get("message-group-not-found"))
        return False

    if repo.is_blocked(group.id, user_id):
        await answer_with_retry(
            message,
            i18n.get("message-blocked-in-group", name=group.name),
        )
        return False

    if not repo.is_member(group.id, user_id):
        repo.add_member(group.id, user_id)
    repo.set_current_group(user_id, group.id)
    await dialog_manager.start(state=MenuSG.group, mode=StartMode.RESET_STACK)
    return True


@router.message(CommandStart())
async def cmd_start(
    message: Message,
    command: CommandObject,
    i18n: TranslatorRunner,
    current_group: Group | None,
    dialog_manager: DialogManager,
) -> None:
    """Обработчик команды /start."""
    user_id = message.from_user.id if message.from_user else 0
    args = (command.args or "").strip()

    if args.startswith("join_"):
        invite_code = args[5:]
        if invite_code:
            await _join_group_by_code(message, invite_code, i18n, user_id, dialog_manager)
            return

    await start_menu(dialog_manager, current_group)


@router.message(Command(commands=["help"]))
async def cmd_help(message: Message, i18n: TranslatorRunner) -> None:
    """Обработчик команды /help."""
    await answer_with_retry(message, i18n.get("help-text"))
