from enum import StrEnum

from aiogram.filters.callback_data import CallbackData


class Action(StrEnum):
    MAIN = "main"
    REGION = "region"
    ABOUT = "about"
    TOURS = "tours"
    TOUR = "tour"


class Nav(CallbackData, prefix="nav"):
    action: Action
    region: str | None = None
    tour: str | None = None

