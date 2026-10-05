from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InputRichMessage

from data.forms import Form
from data.load_data import GetMarkdown
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
        await callback_query.message.edit_text(
            rich_message=InputRichMessage(markdown=await GetMarkdown.about_region_markdown(region)),
            reply_markup=back_keyboard(region),
        )
    if section == "back":
        await callback_query.message.edit_text(
            rich_message=InputRichMessage(markdown=await GetMarkdown.menu_markdown(region)),
            reply_markup=region_keyboard(region),
        )
    if section == "tours":
        await callback_query.message.edit_text(
            rich_message=InputRichMessage(markdown=await GetMarkdown.menu_markdown("tours")),
            reply_markup=tours_keyboard(region)
        )
        await state.set_state(Form.tour_menu)
        
@router.callback_query(Form.tour_menu)
async def tour_menu(callback_query: types.CallbackQuery, state: FSMContext):
    region, tour = callback_query.data.split(":")
    if tour == "back":
        await callback_query.message.edit_text(
            rich_message=InputRichMessage(markdown=await GetMarkdown.menu_markdown(region)),
            reply_markup=region_keyboard(region),
        )
        await state.set_state(Form.region_menu)
    else:
        await callback_query.message.edit_text(
            rich_message=InputRichMessage(markdown=await GetMarkdown.tour_markdown(tour)),
            reply_markup=back_keyboard(region),
        )
        await state.set_state(Form.tour_preview)
        
@router.callback_query(Form.tour_preview)
async def tour_preview(callback_query: types.CallbackQuery, state: FSMContext):
    region = callback_query.data.split(':')[0]
    await callback_query.message.edit_text(
        rich_message=InputRichMessage(
            markdown=await GetMarkdown.menu_markdown("tours")
        ),
        reply_markup=tours_keyboard(region),
    )
    await state.set_state(Form.tour_menu)