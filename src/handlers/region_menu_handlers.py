import aiofiles
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InputRichMessage

from data.forms import Form
from keyboards.navigation_keyboards import (
    back_keyboard,
    region_keyboard,
    tours_keyboard,
)

router = Router()

@router.callback_query(Form.region_menu)
async def region_menu(callback_query: types.CallbackQuery, state: FSMContext):
    region, section = callback_query.data.split(":")
    if section == "about":
        async with aiofiles.open(f"data/markdown/about_region/about_{region}.md") as f:
            markdown_content = await f.read()
        await callback_query.message.edit_text(
            rich_message=InputRichMessage(markdown=markdown_content),
            reply_markup=back_keyboard(region),
        )
    if section == "back":
        async with aiofiles.open(f"data/markdown/menus/main_{region}.md") as f:
            markdown_content = await f.read()
        await callback_query.message.edit_text(
            rich_message=InputRichMessage(markdown=markdown_content),
            reply_markup=region_keyboard(region),
        )
    if section == "tours":
        async with aiofiles.open("data/markdown/menus/tours_menu.md") as f:
            markdown_content = await f.read()
        await callback_query.message.edit_text(
            rich_message=InputRichMessage(markdown=markdown_content),
            reply_markup=tours_keyboard(region)
        )
        await state.set_state(Form.tour_menu)
        
@router.callback_query(Form.tour_menu)
async def tour_menu(callback_query: types.CallbackQuery, state: FSMContext):
    region, tour = callback_query.data.split(":")
    if tour == "back":
        async with aiofiles.open(f"data/markdown/menus/main_{region}.md") as f:
            markdown_content = await f.read()
        await callback_query.message.edit_text(
            rich_message=InputRichMessage(markdown=markdown_content),
            reply_markup=region_keyboard(region),
        )
    else:
        async with aiofiles.open(f"data/markdown/tours/{tour}_tour.md") as f:
            markdown_content = await f.read()
        await callback_query.message.edit_text(
            rich_message=InputRichMessage(markdown=markdown_content),
            reply_markup=back_keyboard(region),
        )
    await state.set_state(Form.region_menu)