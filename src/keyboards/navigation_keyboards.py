from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from data.callbacks import Action, Nav
from utilities.load_data import get_region, get_regions, get_tour


def button(text: str, nav: Nav) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, callback_data=nav.pack())


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [button(region.title, Nav(action=Action.REGION, region=region.slug))]
        for region in get_regions().values()
    ])

cancel_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Отмена", callback_data="cancel")]
])

skip_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Пропустить", callback_data="skip")],
    [InlineKeyboardButton(text="Отмена", callback_data="cancel")]
])


def region_keyboard(region: str | None) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            button("Маршруты", Nav(action=Action.TOURS, region=region)),
            button("О регионе", Nav(action=Action.ABOUT, region=region)),
        ],
        [button("Главное меню", Nav(action=Action.MAIN))],
    ])


def back_to_region_keyboard(region: str | None) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [button("Назад", Nav(action=Action.REGION, region=region))]
    ])


def tours_keyboard(region_slug: str | None) -> InlineKeyboardMarkup:
    region = get_region(region_slug)
    kb = [
        [button(tour.title, Nav(action=Action.TOUR, region=region.slug, tour=tour.slug))]
                for tour in region.tours
    ]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            *kb,
            [button("Назад", Nav(action=Action.REGION, region=region.slug))],
        ]
    )

def tour_pages_keyboard(
        region_slug: str | None,
        tour_slug: str | None,
        page: int) -> InlineKeyboardMarkup:
    region = get_region(region_slug)
    tour = get_tour(region_slug, tour_slug)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                button("⏪️", Nav(action=Action.TOUR, region=region.slug, tour=tour_slug, page=1)),
                button("⬅️", Nav(action=Action.TOUR, region=region.slug, tour=tour_slug, page=page - 1)),
                button("➡️️", Nav(action=Action.TOUR, region=region.slug, tour=tour_slug, page=page + 1)),
                button("⏩", Nav(action=Action.TOUR, region=region.slug, tour=tour_slug, page=tour.pages))
            ],
            [button("К маршрутам", Nav(action=Action.TOURS, region=region.slug))],
        ]
    )
