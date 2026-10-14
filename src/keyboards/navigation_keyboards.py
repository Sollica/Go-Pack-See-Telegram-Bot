from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.data.callbacks import Action, Nav
from src.utilities.load_data import get_region, get_regions, get_tour, get_tour_page_link


def button(text: str, nav: Nav) -> InlineKeyboardButton:
    """Создаёт кнопку с данными для навигации.

    Args:
        text: Текст, отображаемый на кнопке.
        nav: Данные навигации, которые будут переданы при нажатии.

    Returns:
        InlineKeyboardButton: Кнопка с упакованными callback-данными.
    """
    return InlineKeyboardButton(text=text, callback_data=nav.pack())


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Создаёт клавиатуру главного меню со списком регионов.

    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопкой для каждого региона.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [button(region.title, Nav(action=Action.REGION, region=region.slug))]
            for region in get_regions().values()
        ]
    )


# Клавиатура для отмены текущего действия.
cancel_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Отмена", callback_data="cancel")]]
)

# Клавиатура для пропуска необязательного шага или отмены действия.
skip_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Пропустить", callback_data="skip")],
        [InlineKeyboardButton(text="Отмена", callback_data="cancel")],
    ]
)


def region_keyboard(region: str | None) -> InlineKeyboardMarkup:
    """Создаёт клавиатуру меню выбранного региона.

    Args:
        region: Идентификатор региона.

    Returns:
        InlineKeyboardMarkup: Клавиатура с переходами к маршрутам,
            информации о регионе и главному меню.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                button("Маршруты", Nav(action=Action.TOURS, region=region)),
                button("О регионе", Nav(action=Action.ABOUT, region=region)),
            ],
            [button("Главное меню", Nav(action=Action.MAIN))],
        ]
    )


def back_to_region_keyboard(region: str | None) -> InlineKeyboardMarkup:
    """Создаёт клавиатуру для возврата к меню региона.

    Args:
        region: Идентификатор региона.

    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопкой возврата.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[[button("Назад", Nav(action=Action.REGION, region=region))]]
    )


def tours_keyboard(region_slug: str | None) -> InlineKeyboardMarkup:
    """Создаёт клавиатуру со списком экскурсий региона.

    Добавляет кнопку для каждой экскурсии и кнопку возврата
    к меню выбранного региона.

    Args:
        region_slug: Идентификатор региона.

    Returns:
        InlineKeyboardMarkup: Клавиатура со списком экскурсий.
    """
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
    region_slug: str | None, tour_slug: str | None, page: int
) -> InlineKeyboardMarkup:
    """Создаёт клавиатуру навигации по страницам экскурсии.

    Добавляет ссылку на карту, если она доступна, кнопки
    перехода между страницами и кнопку возврата к списку экскурсий.

    Args:
        region_slug: Идентификатор региона.
        tour_slug: Идентификатор экскурсии.
        page: Номер текущей страницы.

    Returns:
        InlineKeyboardMarkup: Клавиатура с элементами навигации
            по экскурсии.
    """
    region = get_region(region_slug)
    tour = get_tour(region_slug, tour_slug)
    url = get_tour_page_link(region_slug, tour_slug, page)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Показать на карте", url=url)] if url else [],
            [
                button("⏪️", Nav(action=Action.TOUR, region=region.slug, tour=tour_slug, page=1)),
                button(
                    "⬅️", Nav(action=Action.TOUR, region=region.slug, tour=tour_slug, page=page - 1)
                ),
                button(
                    "➡️️", Nav(action=Action.TOUR, region=region.slug, tour=tour_slug, page=page + 1)
                ),
                button(
                    "⏩",
                    Nav(action=Action.TOUR, region=region.slug, tour=tour_slug, page=tour.pages),
                ),
            ],
            [button("К маршрутам", Nav(action=Action.TOURS, region=region.slug))],
        ]
    )
