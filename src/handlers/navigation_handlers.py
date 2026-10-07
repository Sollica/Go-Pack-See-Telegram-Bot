from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InputRichMessage, Message

from data.callbacks import Action, Nav
from keyboards.navigation_keyboards import (
    back_to_region_keyboard,
    main_menu_keyboard,
    region_keyboard,
    tour_pages_keyboard,
    tours_keyboard,
)
from utilities.load_data import MarkdownType, get_markdown, get_tour

router = Router()


async def show(callback: CallbackQuery, markdown: str, keyboard: InlineKeyboardMarkup) -> None:
    if not isinstance(callback.message, Message):
        return
    await callback.message.edit_text(
        rich_message=InputRichMessage(markdown=markdown),
        reply_markup=keyboard,
    )


@router.callback_query(Nav.filter(F.action == Action.MAIN))
async def on_main(callback: CallbackQuery) -> None:
    await show(callback, await get_markdown(MarkdownType.MENU, "main"), main_menu_keyboard())


@router.callback_query(Nav.filter(F.action == Action.REGION))
async def on_region(callback: CallbackQuery, callback_data: Nav) -> None:
    await show(
        callback,
        await get_markdown(MarkdownType.MENU,callback_data.region),
        region_keyboard(callback_data.region)
    )



@router.callback_query(Nav.filter(F.action == Action.ABOUT))
async def on_about(callback: CallbackQuery, callback_data: Nav) -> None:
    await show(
        callback,
        await get_markdown(MarkdownType.ABOUT_REGION, callback_data.region),
        back_to_region_keyboard(callback_data.region),
    )


@router.callback_query(Nav.filter(F.action == Action.TOURS))
async def on_tours(callback: CallbackQuery, callback_data: Nav) -> None:
    await show(
        callback,
        await get_markdown(MarkdownType.MENU, "tours"),
        tours_keyboard(callback_data.region)
    )


@router.callback_query(Nav.filter(F.action == Action.TOUR), flags={"manual_answer": True})
async def on_tour(callback: CallbackQuery, callback_data: Nav) -> None:
    page = callback_data.page
    tour = get_tour(callback_data.region, callback_data.tour)
    if page is None:
        page = 1
    if 1 <= page <= tour.pages:
        await callback.answer()
        await show(
            callback,
            await get_markdown(
                MarkdownType.TOUR,
                f"{callback_data.region}_{tour.slug}_{page}"
            ), tour_pages_keyboard(callback_data.region, tour.slug, page)
        )
    else:
        if page < 1:
            await callback.answer(f"Вы находитесь на первой странице: 1/{tour.pages}", show_alert=True)
        else:
            await callback.answer(f"Вы находитесь на последней странице: {tour.pages}/{tour.pages}", show_alert=True)
