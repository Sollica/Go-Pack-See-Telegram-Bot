from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InputRichMessage, Message

from src.data.callbacks import Action, Nav
from src.keyboards.navigation_keyboards import (
    back_to_region_keyboard,
    main_menu_keyboard,
    region_keyboard,
    tour_pages_keyboard,
    tours_keyboard,
)
from src.utilities.load_data import MarkdownType, get_markdown, get_tour

router = Router()


async def show(callback: CallbackQuery, markdown: str, keyboard: InlineKeyboardMarkup) -> None:
    """Обновляет сообщение с содержимым и клавиатурой.

    Если исходное сообщение недоступно для редактирования,
    завершает выполнение без изменений.

    Args:
        callback (CallbackQuery): Callback-запрос, вызвавший обновление сообщения.
        markdown (str): Markdown-текст для отображения.
        keyboard (InlineKeyboardMarkup): Клавиатура, прикрепляемая к сообщению.
    """
    if not isinstance(callback.message, Message):
        return
    await callback.message.edit_text(
        rich_message=InputRichMessage(markdown=markdown),
        reply_markup=keyboard,
    )


@router.callback_query(Nav.filter(F.action == Action.MAIN))
async def on_main(callback: CallbackQuery) -> None:
    """Открывает главное меню по нажатию на кнопку навигации.

    Args:
        callback (CallbackQuery): Callback-запрос от кнопки главного меню.
    """
    await show(callback, await get_markdown(MarkdownType.MENU, "main"), main_menu_keyboard())


@router.callback_query(Nav.filter(F.action == Action.REGION))
async def on_region(callback: CallbackQuery, callback_data: Nav) -> None:
    """Открывает меню выбранного региона.

    Загружает содержимое меню и формирует клавиатуру
    с действиями, доступными для выбранного региона.

    Args:
        callback (CallbackQuery): Callback-запрос от кнопки выбора региона.
        callback_data (Nav): Данные навигации с идентификатором региона.
    """
    await show(
        callback,
        await get_markdown(MarkdownType.MENU, callback_data.region),
        region_keyboard(callback_data.region),
    )


@router.callback_query(Nav.filter(F.action == Action.ABOUT))
async def on_about(callback: CallbackQuery, callback_data: Nav) -> None:
    """Показывает информацию о выбранном регионе.

    Загружает описание региона и добавляет клавиатуру
    для возврата к его меню.

    Args:
        callback (CallbackQuery): Callback-запрос от кнопки информации о регионе.
        callback_data (Nav): Данные навигации с идентификатором региона.
    """
    await show(
        callback,
        await get_markdown(MarkdownType.ABOUT_REGION, callback_data.region),
        back_to_region_keyboard(callback_data.region),
    )


@router.callback_query(Nav.filter(F.action == Action.TOURS))
async def on_tours(callback: CallbackQuery, callback_data: Nav) -> None:
    """Открывает список экскурсий выбранного региона.

    Загружает содержимое страницы экскурсий и формирует
    клавиатуру со списком доступных маршрутов.

    Args:
        callback (CallbackQuery): Callback-запрос от кнопки перехода к экскурсиям.
        callback_data (Nav): Данные навигации с идентификатором региона.
    """
    await show(
        callback,
        await get_markdown(MarkdownType.MENU, "tours"),
        tours_keyboard(callback_data.region),
    )


@router.callback_query(Nav.filter(F.action == Action.TOUR), flags={"manual_answer": True})
async def on_tour(callback: CallbackQuery, callback_data: Nav) -> None:
    """Открывает страницу выбранной экскурсии.

    Определяет текущую страницу маршрута, загружает её содержимое
    и отображает клавиатуру для переключения между страницами.
    Если номер страницы выходит за допустимые границы, показывает
    пользователю уведомление с номером первой или последней страницы.

    Args:
        callback (CallbackQuery): Callback-запрос от кнопки экскурсии или пагинации.
        callback_data (Nav): Данные навигации с идентификаторами региона,
            экскурсии и номером страницы.
    """
    page = callback_data.page
    tour = get_tour(callback_data.region, callback_data.tour)
    if page is None:
        page = 1
    if 1 <= page <= tour.pages:
        await callback.answer()
        await show(
            callback,
            await get_markdown(MarkdownType.TOUR, f"{callback_data.region}_{tour.slug}_{page}"),
            tour_pages_keyboard(callback_data.region, tour.slug, page),
        )
    else:
        if page < 1:
            await callback.answer(
                f"Вы находитесь на первой странице: 1/{tour.pages}", show_alert=True
            )
        else:
            await callback.answer(
                f"Вы находитесь на последней странице: {tour.pages}/{tour.pages}", show_alert=True
            )
