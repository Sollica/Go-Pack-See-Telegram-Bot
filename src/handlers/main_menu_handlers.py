from aiogram import F, Router, types
from aiogram.enums import ParseMode
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, InputMediaPhoto

from data.forms import Form
from data.load_data import load_data
from keyboards.navigation_keyboards import main_menu_keyboard, region_keyboard

BOT_MESSAGES = load_data("data/bot_messages.json")
router = Router()

@router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await message.answer(BOT_MESSAGES["start"], parse_mode=ParseMode.MARKDOWN_V2)
    await main_menu(message, state)

@router.message(Command("main_menu"))
async def main_menu(message: types.Message, state: FSMContext):
    await message.answer_photo(photo=FSInputFile("data/media/main_menu.png"), caption=BOT_MESSAGES["main_menu"], reply_markup=main_menu_keyboard)
    await state.set_state(Form.main_menu)

@router.callback_query(F.data == "main_menu")
async def main_menu_query(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_media(media=InputMediaPhoto(media=FSInputFile("data/media/main_menu.png"), caption=BOT_MESSAGES["main_menu"]), reply_markup=main_menu_keyboard)
    await state.set_state(Form.main_menu)

@router.callback_query(Form.main_menu)
async def choose_region(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_media(
        media=InputMediaPhoto(media=FSInputFile(f"data/media/{callback_query.data}.png")),
        reply_markup=region_keyboard(callback_query.data)
    )
    await state.set_state(Form.region_menu)