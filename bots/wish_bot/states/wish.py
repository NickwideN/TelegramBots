from aiogram.fsm.state import State, StatesGroup


class AddWishSG(StatesGroup):
    waiting_text = State()


class CompleteWishSG(StatesGroup):
    waiting_message = State()
