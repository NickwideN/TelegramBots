from aiogram_dialog import DialogManager
from fluentogram import TranslatorRunner

from bots.wish_bot.services import get_repository
from bots.wish_bot.services.repository import Group, User
from bots.wish_bot.utils.members import member_label


def _visibility_text(i18n: TranslatorRunner, is_public: bool) -> str:
    if is_public:
        return i18n.get("visibility-public")
    return i18n.get("visibility-private")


async def get_no_group_data(
    dialog_manager: DialogManager,
    i18n: TranslatorRunner,
    **kwargs,
) -> dict:
    return {
        "text": i18n.get("message-start-no-group"),
        "button_my_groups": i18n.get("button-my-groups"),
        "button_public_groups": i18n.get("button-public-groups"),
        "button_create_group": i18n.get("button-create-group"),
        "button_language": i18n.get("button-language"),
    }


async def get_group_data(
    dialog_manager: DialogManager,
    i18n: TranslatorRunner,
    user: User,
    current_group: Group | None,
    **kwargs,
) -> dict:
    if current_group is None:
        return {
            "text": i18n.get("message-no-group"),
            "button_groups": i18n.get("button-groups"),
            "button_add_wish": i18n.get("button-make-wish"),
            "button_my_wishes": i18n.get("button-my-wishes"),
            "button_open_wishes": i18n.get("button-open-wishes"),
            "button_my_taken": i18n.get("button-my-taken"),
            "button_subscribe": i18n.get("button-subscribe"),
            "button_archive": i18n.get("button-archive"),
            "button_language": i18n.get("button-language"),
            "is_subscribed": False,
        }

    repo = get_repository()
    subscribed = repo.is_subscribed_wishes(current_group.id, user.telegram_id)
    return {
        "text": i18n.get("message-start-in-group", groupName=current_group.name),
        "button_groups": i18n.get("button-groups"),
        "button_add_wish": i18n.get("button-make-wish"),
        "button_my_wishes": i18n.get("button-my-wishes"),
        "button_open_wishes": i18n.get("button-open-wishes"),
        "button_my_taken": i18n.get("button-my-taken"),
        "button_subscribe": (
            i18n.get("button-unsubscribe") if subscribed else i18n.get("button-subscribe")
        ),
        "button_archive": i18n.get("button-archive"),
        "button_language": i18n.get("button-language"),
        "is_subscribed": subscribed,
    }


async def get_groups_hub_data(
    dialog_manager: DialogManager,
    i18n: TranslatorRunner,
    user: User,
    current_group: Group | None,
    **kwargs,
) -> dict:
    if current_group is None:
        return {
            "text": i18n.get("message-no-group"),
            "button_my_groups": i18n.get("button-my-groups"),
            "button_public_groups": i18n.get("button-public-groups"),
            "button_create_group": i18n.get("button-create-group"),
            "button_group_members": i18n.get("button-group-members"),
            "button_back": i18n.get("button-back"),
            "show_members": False,
        }

    visibility = _visibility_text(i18n, current_group.is_public)
    is_admin = current_group.admin_id == user.telegram_id
    return {
        "text": i18n.get(
            "message-groups-hub",
            name=current_group.name,
            visibility=visibility,
        ),
        "button_my_groups": i18n.get("button-my-groups"),
        "button_public_groups": i18n.get("button-public-groups"),
        "button_create_group": i18n.get("button-create-group"),
        "button_group_members": i18n.get("button-group-members"),
        "button_back": i18n.get("button-back"),
        "show_members": is_admin,
    }


async def get_my_groups_data(
    dialog_manager: DialogManager,
    i18n: TranslatorRunner,
    user: User,
    **kwargs,
) -> dict:
    repo = get_repository()
    groups = repo.list_user_groups(user.telegram_id)
    if groups:
        text = i18n.get("message-my-groups")
    else:
        text = i18n.get("message-no-my-groups")
    return {
        "text": text,
        "groups": [{"id": g.id, "name": g.name} for g in groups],
        "has_groups": bool(groups),
        "button_back": i18n.get("button-back"),
    }


async def get_public_groups_data(
    dialog_manager: DialogManager,
    i18n: TranslatorRunner,
    user: User,
    **kwargs,
) -> dict:
    repo = get_repository()
    groups = [
        g for g in repo.list_public_groups()
        if not repo.is_blocked(g.id, user.telegram_id)
    ]
    return {
        "text": i18n.get("message-public-groups"),
        "empty_text": i18n.get("message-no-public-groups"),
        "groups": [{"id": g.id, "name": g.name} for g in groups],
        "has_groups": bool(groups),
        "button_back": i18n.get("button-back"),
    }


async def get_group_members_data(
    dialog_manager: DialogManager,
    i18n: TranslatorRunner,
    user: User,
    current_group: Group | None,
    **kwargs,
) -> dict:
    if current_group is None or current_group.admin_id != user.telegram_id:
        return {
            "text": i18n.get("message-group-not-admin"),
            "members": [],
            "has_members": False,
            "button_back": i18n.get("button-back"),
        }

    repo = get_repository()
    member_ids = repo.list_group_members(current_group.id)
    blocked_ids = set(repo.list_blocked_members(current_group.id))

    members = []
    for user_id in member_ids:
        label = member_label(user_id)
        is_admin = user_id == current_group.admin_id
        if is_admin:
            button_label = f"{label} — {i18n.get('member-role-admin')}"
            can_action = False
        else:
            button_label = f"{label} — {i18n.get('button-block')}"
            can_action = True
        members.append({
            "id": user_id,
            "button_label": button_label,
            "can_action": can_action,
            "is_blocked": False,
        })

    for user_id in blocked_ids:
        if user_id in {m["id"] for m in members}:
            continue
        label = member_label(user_id)
        members.append({
            "id": user_id,
            "button_label": f"{label} — {i18n.get('button-unblock')}",
            "can_action": True,
            "is_blocked": True,
        })

    return {
        "text": i18n.get("message-group-members-header"),
        "empty_text": i18n.get("message-no-group-members"),
        "members": members,
        "has_members": bool(members),
        "button_back": i18n.get("button-back"),
    }


async def get_language_data(
    dialog_manager: DialogManager,
    i18n: TranslatorRunner,
    **kwargs,
) -> dict:
    return {
        "text": i18n.get("message-choose-language"),
        "languages": [
            {"code": "ru", "name": i18n.get("button-language-russian")},
            {"code": "en", "name": i18n.get("button-language-english")},
        ],
        "button_back": i18n.get("button-back"),
    }


async def get_create_name_data(
    dialog_manager: DialogManager,
    i18n: TranslatorRunner,
    **kwargs,
) -> dict:
    return {
        "text": i18n.get("message-create-group-name"),
        "button_back": i18n.get("button-back"),
    }


async def get_create_visibility_data(
    dialog_manager: DialogManager,
    i18n: TranslatorRunner,
    **kwargs,
) -> dict:
    return {
        "text": i18n.get("message-create-group-visibility"),
        "button_public": i18n.get("button-public"),
        "button_private": i18n.get("button-private"),
        "button_back": i18n.get("button-back"),
    }
