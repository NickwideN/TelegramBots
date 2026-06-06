from aiogram_dialog import DialogManager
from fluentogram import TranslatorRunner

from bots.wish_bot.services import get_repository
from bots.wish_bot.services.repository import Group, User
from bots.wish_bot.utils.bot_info import make_invite_link
from bots.wish_bot.utils.members import member_display_name, member_label, member_short_name
from bots.wish_bot.utils.share import build_share_invite_body, make_telegram_share_url


def _wish_preview(text: str, max_len: int = 10) -> str:
    if len(text) <= max_len:
        return text
    return f"{text[:max_len]}..."


def _author_display(author_id: int) -> tuple[str, str]:
    repo = get_repository()
    author = repo.get_user(author_id)
    name = author.first_name if author and author.first_name else "—"
    username_part = f" (@{author.username})" if author and author.username else ""
    return name, username_part


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
    share_text = build_share_invite_body(i18n, current_group)
    return {
        "text": i18n.get("message-group-created", name=current_group.name, link=link),
        "button_share": i18n.get("button-share"),
        "share_url": make_telegram_share_url(link, share_text),
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
    share_text = build_share_invite_body(i18n, current_group)
    return {
        "text": i18n.get(
            "message-share-group",
            name=current_group.name,
            link=link,
        ),
        "button_share": i18n.get("button-share"),
        "share_url": make_telegram_share_url(link, share_text),
        "button_back": i18n.get("button-back"),
    }


async def get_my_wishes_data(
    dialog_manager: DialogManager,
    i18n: TranslatorRunner,
    user: User,
    current_group: Group | None,
    **kwargs,
) -> dict:
    button_back = i18n.get("button-back")
    if current_group is None:
        return {
            "text": i18n.get("message-no-group"),
            "wishes": [],
            "has_wishes": False,
            "button_back": button_back,
        }

    repo = get_repository()
    wishes = repo.list_wishes_by_author(user.telegram_id, current_group.id)
    if not wishes:
        return {
            "text": i18n.get("message-no-my-wishes"),
            "wishes": [],
            "has_wishes": False,
            "button_back": button_back,
        }

    lines = [i18n.get("message-my-wishes-title"), ""]
    wish_items = []
    for index, wish in enumerate(wishes, start=1):
        lines.append(f"{index}. {wish.text}")
        wish_items.append({
            "id": wish.id,
            "button_label": f"🗑 {index}. {_wish_preview(wish.text)}",
        })
    lines.extend(["", i18n.get("message-my-wishes-delete-prompt")])

    return {
        "text": "\n".join(lines),
        "wishes": wish_items,
        "has_wishes": True,
        "button_back": button_back,
    }


async def get_open_wishes_data(
    dialog_manager: DialogManager,
    i18n: TranslatorRunner,
    user: User,
    current_group: Group | None,
    **kwargs,
) -> dict:
    button_back = i18n.get("button-back")
    if current_group is None:
        return {
            "text": i18n.get("message-no-group"),
            "wishes": [],
            "has_wishes": False,
            "button_back": button_back,
        }

    repo = get_repository()
    wishes = repo.list_open_wishes(
        current_group.id,
        exclude_author_id=user.telegram_id,
    )
    if not wishes:
        return {
            "text": i18n.get("message-no-open-wishes"),
            "wishes": [],
            "has_wishes": False,
            "button_back": button_back,
        }

    lines = [i18n.get("message-open-wishes-header"), ""]
    wish_items = []
    for index, wish in enumerate(wishes, start=1):
        lines.append(f"{index}. {wish.text}")
        wish_items.append({
            "id": wish.id,
            "button_label": f"✋ {index}. {_wish_preview(wish.text)}",
        })
    lines.extend(["", i18n.get("message-open-wishes-take-prompt")])

    return {
        "text": "\n".join(lines),
        "wishes": wish_items,
        "has_wishes": True,
        "button_back": button_back,
    }


async def get_my_taken_data(
    dialog_manager: DialogManager,
    i18n: TranslatorRunner,
    user: User,
    current_group: Group | None,
    **kwargs,
) -> dict:
    button_back = i18n.get("button-back")
    if current_group is None:
        return {
            "text": i18n.get("message-no-group"),
            "wishes": [],
            "has_wishes": False,
            "button_back": button_back,
        }

    repo = get_repository()
    wishes = repo.list_taken_by_user(user.telegram_id, current_group.id)
    if not wishes:
        return {
            "text": i18n.get("message-no-taken-wishes"),
            "wishes": [],
            "has_wishes": False,
            "button_back": button_back,
        }

    lines = [i18n.get("message-taken-wishes-header"), ""]
    wish_items = []
    for index, wish in enumerate(wishes, start=1):
        name, username_part = _author_display(wish.author_id)
        lines.append(f"{index}. {wish.text}")
        lines.append(
            i18n.get("message-taken-wish-for", name=name, usernamePart=username_part),
        )
        lines.append("")
        wish_items.append({
            "id": wish.id,
            "button_label": f"✅ {index}. {_wish_preview(wish.text)}",
        })
    lines.append(i18n.get("message-taken-wishes-complete-prompt"))

    return {
        "text": "\n".join(lines),
        "wishes": wish_items,
        "has_wishes": True,
        "button_back": button_back,
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


def _member_wish_stats(repo, user_id: int, group_id: int) -> tuple[int, int, int, int]:
    wishes_count = len(repo.list_wishes_by_author(user_id, group_id))
    wishes_completed_by_others = len(
        repo.list_completed_wishes_by_author(user_id, group_id),
    )
    taken_wishes_count = len(repo.list_taken_by_user(user_id, group_id))
    fulfilled_others_count = len(
        repo.list_completed_wishes_by_taker(user_id, group_id),
    )
    return (
        wishes_count,
        wishes_completed_by_others,
        taken_wishes_count,
        fulfilled_others_count,
    )


async def get_group_members_data(
    dialog_manager: DialogManager,
    i18n: TranslatorRunner,
    user: User,
    current_group: Group | None,
    **kwargs,
) -> dict:
    button_back = i18n.get("button-back")
    if current_group is None or current_group.admin_id != user.telegram_id:
        return {
            "text": i18n.get("message-group-not-admin"),
            "members": [],
            "has_members": False,
            "button_back": button_back,
        }

    repo = get_repository()
    member_ids = repo.list_group_members(current_group.id)
    blocked_ids = set(repo.list_blocked_members(current_group.id))

    admins: list[int] = []
    regular: list[int] = []
    blocked: list[int] = []

    for user_id in member_ids:
        if user_id in blocked_ids:
            blocked.append(user_id)
        elif user_id == current_group.admin_id:
            admins.append(user_id)
        else:
            regular.append(user_id)

    for user_id in blocked_ids:
        if user_id not in member_ids:
            blocked.append(user_id)

    lines = [
        i18n.get("message-group-members-title", groupName=current_group.name),
        "",
    ]
    members: list[dict] = []
    index = 1

    if admins:
        lines.append(i18n.get("message-group-members-admins-header"))
        for user_id in admins:
            lines.append(
                i18n.get(
                    "message-group-members-admin-line",
                    name=member_short_name(user_id),
                ),
            )
            members.append({
                "id": user_id,
                "button_label": f"{index}. {member_short_name(user_id)} 👑",
            })
            index += 1
        lines.append("")

    if regular:
        lines.append(i18n.get("message-group-members-members-header"))
        for user_id in regular:
            lines.append(f"{index}. {member_label(user_id)}")
            members.append({
                "id": user_id,
                "button_label": f"{index}. {member_short_name(user_id)}",
            })
            index += 1
        lines.append("")

    if blocked:
        lines.append(i18n.get("message-group-members-blocked-header"))
        for user_id in blocked:
            lines.append(f"{index}. {member_label(user_id)}")
            members.append({
                "id": user_id,
                "button_label": f"{index}. {member_short_name(user_id)} 🚫",
            })
            index += 1
        lines.append("")

    if members:
        lines.append(i18n.get("message-group-members-select-prompt"))

    return {
        "text": "\n".join(lines) if members else i18n.get("message-no-group-members"),
        "members": members,
        "has_members": bool(members),
        "button_back": button_back,
    }


async def get_group_member_detail_data(
    dialog_manager: DialogManager,
    i18n: TranslatorRunner,
    user: User,
    current_group: Group | None,
    **kwargs,
) -> dict:
    button_back = i18n.get("button-back")
    if current_group is None or current_group.admin_id != user.telegram_id:
        return {
            "text": i18n.get("message-group-not-admin"),
            "show_toggle": False,
            "button_toggle": "",
            "button_back": button_back,
        }

    target_id = dialog_manager.dialog_data.get("selected_member_id")
    if not target_id:
        return {
            "text": i18n.get("message-member-not-found"),
            "show_toggle": False,
            "button_toggle": "",
            "button_back": button_back,
        }

    target_id = int(target_id)
    repo = get_repository()
    is_admin = target_id == current_group.admin_id
    is_blocked = repo.is_blocked(current_group.id, target_id)

    (
        wishes_count,
        wishes_completed_by_others,
        taken_wishes_count,
        fulfilled_others_count,
    ) = _member_wish_stats(repo, target_id, current_group.id)

    if is_admin:
        role = i18n.get("member-role-admin")
    else:
        role = i18n.get("member-role-participant")

    status = (
        i18n.get("member-status-blocked")
        if is_blocked
        else i18n.get("member-status-active")
    )

    if is_blocked:
        button_toggle = f"✅ {i18n.get('button-unblock')}"
    else:
        button_toggle = f"🚫 {i18n.get('button-block')}"

    return {
        "text": i18n.get(
            "message-group-member-detail",
            name=member_display_name(target_id),
            role=role,
            status=status,
            wishesCount=wishes_count,
            wishesCompletedByOthers=wishes_completed_by_others,
            takenWishesCount=taken_wishes_count,
            fulfilledOthersCount=fulfilled_others_count,
        ),
        "show_toggle": not is_admin,
        "button_toggle": button_toggle,
        "button_back": button_back,
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
