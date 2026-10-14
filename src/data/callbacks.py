from enum import StrEnum

from aiogram.filters.callback_data import CallbackData


class Action(StrEnum):
    """Определяет действия для навигации по боту."""

    MAIN = "main"
    REGION = "region"
    ABOUT = "about"
    TOURS = "tours"
    TOUR = "tour"


class Nav(CallbackData, prefix="nav"):
    """Хранит данные навигации для callback-запросов."""

    action: Action
    region: str | None = None
    tour: str | None = None
    page: int | None = None
