from aiogram.fsm.state import State, StatesGroup


class SettingSG(StatesGroup):
    start = State()
    url_copy = State()


class StartSG(StatesGroup):
    start = State()
    hb_today = State()
