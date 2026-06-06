from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import (
    Back,
    Button,
    ListGroup,
    Row,
    Select,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Format

from bots.wish_bot.dialogs.menu.getters import (
    get_create_name_data,
    get_create_visibility_data,
    get_group_data,
    get_group_members_data,
    get_groups_hub_data,
    get_language_data,
    get_my_groups_data,
    get_no_group_data,
    get_public_groups_data,
)
from bots.wish_bot.dialogs.menu.handlers import (
    on_add_wish,
    on_archive,
    on_create_group_name,
    on_create_group_private,
    on_create_group_public,
    on_language_back,
    on_member_action,
    on_my_taken,
    on_my_wishes,
    on_open_language,
    on_open_wishes,
    on_select_language,
    on_select_my_group,
    on_select_public_group,
    on_subscribe_toggle,
)
from bots.wish_bot.states.menu import MenuSG

no_group_window = Window(
    Format("{text}"),
    SwitchTo(
        Format("{button_my_groups}"),
        id="my_groups",
        state=MenuSG.my_groups,
    ),
    SwitchTo(
        Format("{button_public_groups}"),
        id="public_groups",
        state=MenuSG.public_groups,
    ),
    SwitchTo(
        Format("{button_create_group}"),
        id="create_group",
        state=MenuSG.create_name,
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
    SwitchTo(
        Format("{button_groups}"),
        id="groups_hub",
        state=MenuSG.groups_hub,
    ),
    Button(
        Format("{button_subscribe}"),
        id="subscribe_toggle",
        on_click=on_subscribe_toggle,
    ),
    Button(
        Format("{button_archive}"),
        id="archive",
        on_click=on_archive,
    ),
    Button(
        Format("{button_language}"),
        id="language",
        on_click=on_open_language,
    ),
    getter=get_group_data,
    state=MenuSG.group,
)

groups_hub_window = Window(
    Format("{text}"),
    SwitchTo(
        Format("{button_my_groups}"),
        id="my_groups",
        state=MenuSG.my_groups,
    ),
    SwitchTo(
        Format("{button_public_groups}"),
        id="public_groups",
        state=MenuSG.public_groups,
    ),
    SwitchTo(
        Format("{button_create_group}"),
        id="create_group",
        state=MenuSG.create_name,
    ),
    SwitchTo(
        Format("{button_group_members}"),
        id="group_members",
        state=MenuSG.group_members,
        when="show_members",
    ),
    Back(Format("{button_back}")),
    getter=get_groups_hub_data,
    state=MenuSG.groups_hub,
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
    Back(Format("{button_back}")),
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
    Back(Format("{button_back}")),
    getter=get_public_groups_data,
    state=MenuSG.public_groups,
)

group_members_window = Window(
    Format("{text}"),
    Format("{empty_text}", when="not has_members"),
    ListGroup(
        Button(
            Format("{item[button_label]}"),
            id="member_action",
            on_click=on_member_action,
        ),
        id="members_list",
        item_id_getter=lambda item: str(item["id"]),
        items="members",
        when="has_members",
    ),
    Back(Format("{button_back}")),
    getter=get_group_members_data,
    state=MenuSG.group_members,
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
    Back(Format("{button_back}")),
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
    Back(Format("{button_back}")),
    getter=get_create_visibility_data,
    state=MenuSG.create_visibility,
)

menu_dialog = Dialog(
    no_group_window,
    group_window,
    groups_hub_window,
    my_groups_window,
    public_groups_window,
    group_members_window,
    language_window,
    create_name_window,
    create_visibility_window,
)
