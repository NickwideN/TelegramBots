from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import (
    Button,
    Group,
    ListGroup,
    Row,
    Select,
    Url,
)
from aiogram_dialog.widgets.text import Format

from bots.wish_bot.dialogs.menu.getters import (
    get_create_name_data,
    get_create_visibility_data,
    get_group_created_data,
    get_group_data,
    get_group_member_detail_data,
    get_group_members_data,
    get_groups_select_data,
    get_language_data,
    get_my_taken_data,
    get_my_wishes_data,
    get_my_groups_data,
    get_open_wishes_data,
    get_no_group_data,
    get_public_groups_data,
    get_share_group_data,
    get_welcome_data,
    get_welcome_invite_data,
    get_welcome_invite_invalid_data,
)
from bots.wish_bot.dialogs.menu.handlers import (
    on_add_wish,
    on_archive,
    on_create_group_name,
    on_create_group_private,
    on_complete_taken_wish,
    on_create_group_public,
    on_delete_my_wish,
    on_language_back,
    on_member_block_toggle,
    on_select_member,
    on_my_taken,
    on_my_wishes,
    on_nav_back,
    on_open_create_group,
    on_open_groups_select,
    on_open_language,
    on_open_members,
    on_open_my_groups,
    on_open_public_groups,
    on_open_share,
    on_open_wishes,
    on_take_open_wish,
    on_select_language,
    on_select_my_group,
    on_select_public_group,
    on_subscribe_toggle,
    on_welcome_start,
)
from bots.wish_bot.states.menu import MenuSG

welcome_window = Window(
    Format("{text}"),
    Button(
        Format("{button_start}"),
        id="welcome_start",
        on_click=on_welcome_start,
    ),
    getter=get_welcome_data,
    state=MenuSG.welcome,
)

welcome_invite_window = Window(
    Format("{text}"),
    Button(
        Format("{button_start}"),
        id="welcome_invite_start",
        on_click=on_welcome_start,
    ),
    getter=get_welcome_invite_data,
    state=MenuSG.welcome_invite,
)

welcome_invite_invalid_window = Window(
    Format("{text}"),
    Button(
        Format("{button_start}"),
        id="welcome_invite_invalid_start",
        on_click=on_welcome_start,
    ),
    getter=get_welcome_invite_invalid_data,
    state=MenuSG.welcome_invite_invalid,
)

no_group_window = Window(
    Format("{text}"),
    Button(
        Format("{button_my_groups}"),
        id="my_groups",
        on_click=on_open_my_groups,
    ),
    Button(
        Format("{button_public_groups}"),
        id="public_groups",
        on_click=on_open_public_groups,
    ),
    Button(
        Format("{button_create_group}"),
        id="create_group",
        on_click=on_open_create_group,
    ),
    Button(
        Format("{button_language}"),
        id="language",
        on_click=on_open_language,
    ),
    getter=get_no_group_data,
    state=MenuSG.no_group,
)

group_window = Window(
    Format("{text}"),
    Row(
        Button(
            Format("{button_add_wish}"),
            id="add_wish",
            on_click=on_add_wish,
        ),
        Button(
            Format("{button_my_wishes}"),
            id="my_wishes",
            on_click=on_my_wishes,
        ),
    ),
    Row(
        Button(
            Format("{button_open_wishes}"),
            id="open_wishes",
            on_click=on_open_wishes,
        ),
        Button(
            Format("{button_my_taken}"),
            id="my_taken",
            on_click=on_my_taken,
        ),
    ),
    Button(
        Format("{button_archive}"),
        id="archive",
        on_click=on_archive,
    ),
    Button(
        Format("{button_subscribe}"),
        id="subscribe_toggle",
        on_click=on_subscribe_toggle,
    ),
    Button(
        Format("{button_share_group}"),
        id="share_group",
        on_click=on_open_share,
        when="show_share",
    ),
    Button(
        Format("{button_group_members}"),
        id="group_members",
        on_click=on_open_members,
        when="show_members",
    ),
    Button(
        Format("{button_groups}"),
        id="groups_select",
        on_click=on_open_groups_select,
    ),
    Button(
        Format("{button_language}"),
        id="language",
        on_click=on_open_language,
    ),
    getter=get_group_data,
    state=MenuSG.group,
)

my_wishes_window = Window(
    Format("{text}"),
    Group(
        ListGroup(
            Button(
                Format("{item[button_label]}"),
                id="delete_my_wish",
                on_click=on_delete_my_wish,
            ),
            id="my_wishes_list",
            item_id_getter=lambda item: str(item["id"]),
            items="wishes",
        ),
        width=1,
        when="has_wishes",
    ),
    Button(
        Format("{button_back}"),
        id="my_wishes_back",
        on_click=on_nav_back,
    ),
    getter=get_my_wishes_data,
    state=MenuSG.my_wishes,
)

open_wishes_window = Window(
    Format("{text}"),
    Group(
        ListGroup(
            Button(
                Format("{item[button_label]}"),
                id="take_open_wish",
                on_click=on_take_open_wish,
            ),
            id="open_wishes_list",
            item_id_getter=lambda item: str(item["id"]),
            items="wishes",
        ),
        width=1,
        when="has_wishes",
    ),
    Button(
        Format("{button_back}"),
        id="open_wishes_back",
        on_click=on_nav_back,
    ),
    getter=get_open_wishes_data,
    state=MenuSG.open_wishes,
)

my_taken_window = Window(
    Format("{text}"),
    Group(
        ListGroup(
            Button(
                Format("{item[button_label]}"),
                id="complete_taken_wish",
                on_click=on_complete_taken_wish,
            ),
            id="my_taken_list",
            item_id_getter=lambda item: str(item["id"]),
            items="wishes",
        ),
        width=1,
        when="has_wishes",
    ),
    Button(
        Format("{button_back}"),
        id="my_taken_back",
        on_click=on_nav_back,
    ),
    getter=get_my_taken_data,
    state=MenuSG.my_taken,
)

groups_select_window = Window(
    Format("{text}"),
    Button(
        Format("{button_my_groups}"),
        id="my_groups",
        on_click=on_open_my_groups,
    ),
    Button(
        Format("{button_public_groups}"),
        id="public_groups",
        on_click=on_open_public_groups,
    ),
    Button(
        Format("{button_create_group}"),
        id="create_group",
        on_click=on_open_create_group,
    ),
    Button(
        Format("{button_back}"),
        id="groups_select_back",
        on_click=on_nav_back,
    ),
    getter=get_groups_select_data,
    state=MenuSG.groups_select,
)

share_group_window = Window(
    Format("{text}"),
    Url(
        Format("{button_share}"),
        Format("{share_url}"),
        id="share_invite",
    ),
    Button(
        Format("{button_back}"),
        id="share_back",
        on_click=on_nav_back,
    ),
    getter=get_share_group_data,
    state=MenuSG.share_group,
)

my_groups_window = Window(
    Format("{text}"),
    ListGroup(
        Button(
            Format("{item[name]}"),
            id="select_my_group",
            on_click=on_select_my_group,
        ),
        id="my_groups_list",
        item_id_getter=lambda item: str(item["id"]),
        items="groups",
        when="has_groups",
    ),
    Button(
        Format("{button_back}"),
        id="my_groups_back",
        on_click=on_nav_back,
    ),
    getter=get_my_groups_data,
    state=MenuSG.my_groups,
)

public_groups_window = Window(
    Format("{text}"),
    Format("{empty_text}", when="not has_groups"),
    ListGroup(
        Button(
            Format("{item[name]}"),
            id="select_public_group",
            on_click=on_select_public_group,
        ),
        id="public_groups_list",
        item_id_getter=lambda item: str(item["id"]),
        items="groups",
        when="has_groups",
    ),
    Button(
        Format("{button_back}"),
        id="public_groups_back",
        on_click=on_nav_back,
    ),
    getter=get_public_groups_data,
    state=MenuSG.public_groups,
)

group_members_window = Window(
    Format("{text}"),
    Group(
        ListGroup(
            Button(
                Format("{item[button_label]}"),
                id="select_member",
                on_click=on_select_member,
            ),
            id="members_list",
            item_id_getter=lambda item: str(item["id"]),
            items="members",
        ),
        width=3,
        when="has_members",
    ),
    Button(
        Format("{button_back}"),
        id="members_back",
        on_click=on_nav_back,
    ),
    getter=get_group_members_data,
    state=MenuSG.group_members,
)

group_member_detail_window = Window(
    Format("{text}"),
    Button(
        Format("{button_toggle}"),
        id="member_toggle",
        on_click=on_member_block_toggle,
        when="show_toggle",
    ),
    Button(
        Format("{button_back}"),
        id="member_detail_back",
        on_click=on_nav_back,
    ),
    getter=get_group_member_detail_data,
    state=MenuSG.group_member_detail,
)

language_window = Window(
    Format("{text}"),
    Select(
        Format("{item[name]}"),
        id="language_select",
        item_id_getter=lambda item: item["code"],
        items="languages",
        on_click=on_select_language,
    ),
    Button(
        Format("{button_back}"),
        id="language_back",
        on_click=on_language_back,
    ),
    getter=get_language_data,
    state=MenuSG.language,
)

create_name_window = Window(
    Format("{text}"),
    MessageInput(on_create_group_name),
    Button(
        Format("{button_back}"),
        id="create_name_back",
        on_click=on_nav_back,
    ),
    getter=get_create_name_data,
    state=MenuSG.create_name,
)

create_visibility_window = Window(
    Format("{text}"),
    Row(
        Button(
            Format("{button_public}"),
            id="create_public",
            on_click=on_create_group_public,
        ),
        Button(
            Format("{button_private}"),
            id="create_private",
            on_click=on_create_group_private,
        ),
    ),
    Button(
        Format("{button_back}"),
        id="create_visibility_back",
        on_click=on_nav_back,
    ),
    getter=get_create_visibility_data,
    state=MenuSG.create_visibility,
)

group_created_window = Window(
    Format("{text}"),
    Url(
        Format("{button_share}"),
        Format("{share_url}"),
        id="share_invite_created",
    ),
    getter=get_group_created_data,
    state=MenuSG.group_created,
)

menu_dialog = Dialog(
    welcome_window,
    welcome_invite_window,
    welcome_invite_invalid_window,
    no_group_window,
    group_window,
    my_wishes_window,
    open_wishes_window,
    my_taken_window,
    groups_select_window,
    share_group_window,
    my_groups_window,
    public_groups_window,
    group_members_window,
    group_member_detail_window,
    language_window,
    create_name_window,
    create_visibility_window,
    group_created_window,
)
