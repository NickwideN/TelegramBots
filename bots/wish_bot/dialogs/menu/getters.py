from aiogram_dialog import DialogManager
from fluentogram import TranslatorRunner

from bots.wish_bot.services import get_repository
from bots.wish_bot.services.repository import Group, User
from bots.wish_bot.utils.bot_info import make_invite_link
from bots.wish_bot.utils.members import member_label
from bots.wish_bot.utils.share import build_share_invite_text, make_telegram_share_url


async def get_welcome_data(
    dialog_manager: DialogManager,
    i18n: TranslatorRunner,
    **kwargs,
) -> dict:
    return {
        "text": i18n.get("message-welcome"),
        "button_start": i18n.get("button-start"),
    }


async def get_welcome_invite_data(
    dialog_manager: DialogManager,
    i18n: TranslatorRunner,
    **kwargs,
) -> dict:
    start_data = dialog_manager.start_data or {}
    group_name = start_data.get("group_name", "")
    if not group_name:
        invite_code = start_data.get("invite_code", "").strip()
        if invite_code:
            group = get_repository().get_group_by_invite(invite_code)
            if group:
                group_name = group.name

    return {
        "text": i18n.get("message-welcome-invite", groupName=group_name),
        "button_start": i18n.get("button-start"),
    }


async def get_welcome_invite_invalid_data(
    dialog_manager: DialogManager,
    i18n: TranslatorRunner,
    **kwargs,
) -> dict:
    return {
        "text": i18n.get("message-welcome-invite-invalid"),
        "button_start": i18n.get("button-start"),
    }


async def get_no_group_data(
    dialog_manager: DialogManager,
    i18n: TranslatorRunner,
    **kwargs,
) -> dict:
    return {
        "text": i18n.get("message-menu-no-group"),
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
    base = {
        "button_add_wish": i18n.get("button-make-wish"),
        "button_my_wishes": i18n.get("button-my-wishes"),
        "button_open_wishes": i18n.get("button-open-wishes"),
        "button_my_taken": i18n.get("button-my-taken"),
        "button_archive": i18n.get("button-archive"),
        "button_subscribe": i18n.get("button-subscribe"),
        "button_share_group": "",
        "button_group_members": i18n.get("button-group-members"),
        "button_groups": i18n.get("button-groups"),
        "button_language": i18n.get("button-language"),
        "show_share": False,
        "show_members": False,
    }

    if current_group is None:
        return {
            **base,
            "text": i18n.get("message-no-group"),
        }

    repo = get_repository()
    subscribed = repo.is_subscribed_wishes(current_group.id, user.telegram_id)
    is_admin = current_group.admin_id == user.telegram_id
    show_share = current_group.is_public or is_admin
    if show_share and not current_group.is_public:
        button_share_group = i18n.get("button-share-group-admin")
    elif show_share:
        button_share_group = i18n.get("button-share-group")
    else:
        button_share_group = ""

    if is_admin:
        member_count = len(repo.list_group_members(current_group.id))
        text = i18n.get(
            "message-menu-group-admin",
            groupName=current_group.name,
            memberCount=member_count,
        )
    else:
        text = i18n.get("message-menu-group-member", groupName=current_group.name)

    return {
        **base,
        "text": text,
        "button_subscribe": (
            i18n.get("button-unsubscribe") if subscribed else i18n.get("button-subscribe")
        ),
        "button_share_group": button_share_group,
        "show_share": show_share,
        "show_members": is_admin,
    }


async def get_groups_select_data(
    dialog_manager: DialogManager,
    i18n: TranslatorRunner,
    **kwargs,
) -> dict:
    return {
        "text": i18n.get("message-groups-select"),
        "button_my_groups": i18n.get("button-my-groups"),
        "button_public_groups": i18n.get("button-public-groups"),
        "button_create_group": i18n.get("button-create-group"),
        "button_back": i18n.get("button-back"),
    }


async def get_group_created_data(
    dialog_manager: DialogManager,
    i18n: TranslatorRunner,
    current_group: Group | None,
    **kwargs,
) -> dict:
    if current_group is None:
        return {
            "text": i18n.get("message-no-group"),
            "button_share": i18n.get("button-share"),
            "share_url": "",
        }

    link = make_invite_link(current_group.invite_code)
    invite_text = build_share_invite_text(i18n, current_group, link)
    return {
        "text": i18n.get("message-group-created", name=current_group.name, link=link),
        "button_share": i18n.get("button-share"),
        "share_url": make_telegram_share_url(invite_text),
    }


async def get_share_group_data(
    dialog_manager: DialogManager,
    i18n: TranslatorRunner,
    current_group: Group | None,
    **kwargs,
) -> dict:
    if current_group is None:
        return {
            "text": i18n.get("message-no-group"),
            "button_share": i18n.get("button-share"),
            "share_url": "",
            "button_back": i18n.get("button-back"),
        }

    link = make_invite_link(current_group.invite_code)
    invite_text = build_share_invite_text(i18n, current_group, link)
    return {
        "text": i18n.get(
            "message-share-group",
            name=current_group.name,
            link=link,
        ),
        "button_share": i18n.get("button-share"),
        "share_url": make_telegram_share_url(invite_text),
        "button_back": i18n.get("button-back"),
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
        else:
            button_label = f"{label} — {i18n.get('button-block')}"
        members.append({
            "id": user_id,
            "button_label": button_label,
            "can_action": not is_admin,
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
