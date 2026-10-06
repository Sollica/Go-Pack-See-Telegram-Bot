from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InputRichMessage

from data.forms import Form
from data.load_data import GetMarkdown
from keyboards.navigation_keyboards import main_menu_keyboard, region_keyboard

router = Router()

@router.callback_query(F.data == "main_menu")
async def main_menu_query(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text(rich_message=InputRichMessage(markdown=await GetMarkdown.menu_markdown("main")), reply_markup=main_menu_keyboard)
    await state.set_state(Form.main_menu)

@router.callback_query(Form.main_menu)
async def choose_region(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text(rich_message=InputRichMessage(markdown=await GetMarkdown.menu_markdown(callback_query.data)),
        reply_markup=region_keyboard(callback_query.data)
    )
    await state.set_state(Form.region_menu)
