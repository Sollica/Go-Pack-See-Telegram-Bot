from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, InputMediaPhoto

from data.forms import Form
from data.load_data import load_data
from keyboards.navigation_keyboards import (
    back_keyboard,
    region_keyboard,
    tours_keyboard,
)

BOT_MESSAGES = load_data("data/bot_messages.json")
router = Router()

@router.callback_query(Form.region_menu)
async def region_menu(callback_query: types.CallbackQuery, state: FSMContext):
    region, section = callback_query.data.split(":")
    if section == "about":
        await callback_query.message.edit_caption(
            caption=BOT_MESSAGES["about_region"][region],
            reply_markup=back_keyboard(region)
        )
    if section == "back":
        await callback_query.message.edit_caption(
            reply_markup=region_keyboard(region)
        )
    if section == "tours":
        await callback_query.message.edit_caption(caption=BOT_MESSAGES["choose_tour"], reply_markup=tours_keyboard(region))