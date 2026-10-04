import aiofiles
from aiogram import F, Router, types
from aiogram.enums import ParseMode
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InputRichMessage

from data.forms import Form
from keyboards.navigation_keyboards import main_menu_keyboard, region_keyboard

router = Router()

@router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await message.answer("Добро пожаловать в *_Go, Pack & See\\!_*\n\nИспользуйте встроенную клавиатуру для навигации по меню и изучайте регионы России с нами\\!", parse_mode=ParseMode.MARKDOWN_V2)
    await main_menu(message, state)

@router.message(Command("main_menu"))
async def main_menu(message: types.Message, state: FSMContext):
    async with aiofiles.open("data/markdown/menus/main_menu.md") as f:
        markdown_content = await f.read()
    await message.answer_rich(InputRichMessage(markdown=markdown_content), reply_markup=main_menu_keyboard)
    await state.set_state(Form.main_menu)

@router.callback_query(F.data == "main_menu")
async def main_menu_query(callback_query: types.CallbackQuery, state: FSMContext):
    async with aiofiles.open("data/markdown/menus/main_menu.md") as f:
        markdown_content = await f.read()
    await callback_query.message.edit_text(rich_message=InputRichMessage(markdown=markdown_content), reply_markup=main_menu_keyboard)
    await state.set_state(Form.main_menu)

@router.callback_query(Form.main_menu)
async def choose_region(callback_query: types.CallbackQuery, state: FSMContext):
    async with aiofiles.open(f"data/markdown/menus/main_{callback_query.data}.md") as f:
        markdown_content = await f.read()
    await callback_query.message.edit_text(rich_message=InputRichMessage(markdown=markdown_content),
        reply_markup=region_keyboard(callback_query.data)
    )
    await state.set_state(Form.region_menu)
