from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from data.load_data import load_data

TOURS = load_data("data/tours.json")

main_menu_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Москва", callback_data="moscow")]
])

def region_keyboard(region: str | None):
    return InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Маршруты", callback_data=f"{region}:tours"), InlineKeyboardButton(text="О регионе", callback_data=f"{region}:about")],
    [InlineKeyboardButton(text="Главное меню", callback_data="main_menu")]
])

def back_keyboard(region: str | None):
    return InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Назад", callback_data=f"{region}:back")]
])

def tours_keyboard(region: str | None):
    kb = [[InlineKeyboardButton(text=tour_name, callback_data=f"{region}:{tour}")] for tour_name, tour in TOURS[region]]
    return InlineKeyboardMarkup(inline_keyboard=kb + [
    [InlineKeyboardButton(text="Назад", callback_data=f"{region}:back")]
])