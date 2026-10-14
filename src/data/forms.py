from aiogram.fsm.state import State, StatesGroup


class Form(StatesGroup):
    """Определяет состояния для обработки пользовательских обращений.

    Attributes:
        suggest_region_name: Ожидание названия предлагаемого региона.
        suggest_tour: Ожидание предложения новой экскурсии.
        bug_report: Ожидание описания обнаруженной ошибки.
    """

    suggest_region_name = State()
    suggest_tour = State()
    bug_report = State()
