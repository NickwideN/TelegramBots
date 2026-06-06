from aiogram.fsm.state import State, StatesGroup


class MenuSG(StatesGroup):
    welcome = State()
    welcome_invite = State()
    welcome_invite_invalid = State()
    no_group = State()
    group = State()
    my_wishes = State()
    open_wishes = State()
    my_taken = State()
    groups_select = State()
    share_group = State()
    my_groups = State()
    public_groups = State()
    group_members = State()
    language = State()
    create_name = State()
    create_visibility = State()
    group_created = State()
