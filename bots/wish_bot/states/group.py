from aiogram.fsm.state import State, StatesGroup


class CreateGroupSG(StatesGroup):
    waiting_name = State()
    waiting_visibility = State()
