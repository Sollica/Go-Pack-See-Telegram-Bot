from aiogram.fsm.state import State, StatesGroup


class Form(StatesGroup):
    main_menu = State()
    region_menu = State()
    tour_menu = State()
    tour_preview = State()
    suggest_region_name = State()
    suggest_tour = State()