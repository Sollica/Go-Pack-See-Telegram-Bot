from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InputRichMessage, Message

from data.callbacks import Action, Nav
from keyboards.navigation_keyboards import (
    back_to_region_keyboard,
    back_to_tours_keyboard,
    main_menu_keyboard,
    region_keyboard,
    tours_keyboard,
)
from utilities.load_data import MarkdownType, get_markdown

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
    await show(callback, await get_markdown(MarkdownType.MENU, callback_data.region), region_keyboard(callback_data.region))


@router.callback_query(Nav.filter(F.action == Action.ABOUT))
async def on_about(callback: CallbackQuery, callback_data: Nav) -> None:
    await show(
        callback,
        await get_markdown(MarkdownType.ABOUT_REGION, callback_data.region),
        back_to_region_keyboard(callback_data.region),
    )


@router.callback_query(Nav.filter(F.action == Action.TOURS))
async def on_tours(callback: CallbackQuery, callback_data: Nav) -> None:
    await show(callback, await get_markdown(MarkdownType.MENU, "tours"), tours_keyboard(callback_data.region))


@router.callback_query(Nav.filter(F.action == Action.TOUR))
async def on_tour(callback: CallbackQuery, callback_data: Nav) -> None:
    await show(
        callback,
        await get_markdown(MarkdownType.TOUR, f"{callback_data.region}_{callback_data.tour}"),
        back_to_tours_keyboard(callback_data.region)
    )
