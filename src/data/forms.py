from aiogram.fsm.state import State, StatesGroup


class Form(StatesGroup):
    main_menu = State()
    region_menu = State()
    tour_menu = State()