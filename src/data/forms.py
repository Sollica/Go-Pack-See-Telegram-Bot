from aiogram.fsm.state import State, StatesGroup


class Form(StatesGroup):
    suggest_region_name = State()
    suggest_tour = State()
    bug_report = State()