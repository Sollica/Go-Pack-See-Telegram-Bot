from aiogram import Router, types
from aiogram.enums import ParseMode
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InputRichMessage, Message

from data.forms import Form
from data.load_data import GetMarkdown, put_data
from keyboards.navigation_keyboards import (
    cancel_keyboard,
    main_menu_keyboard,
    skip_keyboard,
)

router = Router()

@router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await message.answer((
        "Добро пожаловать в *_Go, Pack & See\\!_*\n\n"""
         "Используйте встроенную клавиатуру для навигации "
         "по меню и изучайте регионы России с нами\\!"
    ), parse_mode=ParseMode.MARKDOWN_V2)
    await main_menu(message, state)

@router.message(Command("main_menu"))
async def main_menu(message: types.Message, state: FSMContext):
    await message.answer_rich(InputRichMessage(markdown=await GetMarkdown.menu_markdown("main")), reply_markup=main_menu_keyboard)
    await state.set_state(Form.main_menu)

@router.message(Command("suggest"))
async def suggest(message: types.Message, state: FSMContext):
    await message.answer((
        "Хотите увидеть новый регион в нашем проекте? "
        "Поделитесь своими пожеланиями с нами!\n\n"
        "Напишите название региона, который нам стоит добавить в проект."
    ), reply_markup=cancel_keyboard)
    await state.set_state(Form.suggest_region_name)

@router.message(Form.suggest_region_name)
@router.callback_query(Form.suggest_region_name)
async def suggest_region(event: Message | CallbackQuery, state: FSMContext):
    if isinstance(event, CallbackQuery):
        await event.message.edit_text("Запрос на добавление региона отменён.")
        await state.clear()
    else:
        await state.update_data(suggested_region_name=event.text)
        await event.answer((
            f"Если у вас есть идеи насчёт конкретного маршрута "
            f"для региона «{event.text}», пожалуйста, напишите их ниже."
        ), reply_markup=skip_keyboard)
        await state.set_state(Form.suggest_tour)

@router.message(Form.suggest_tour)
@router.callback_query(Form.suggest_tour)
async def suggest_tour(event: Message | CallbackQuery, state: FSMContext):
    tour = None
    if isinstance(event, CallbackQuery):
        if event.data == "skip":
            await event.message.edit_text("Запрос на добавление региона сохранён.")
            tour = ""
        else:
            await event.message.edit_text("Запрос на добавление региона отменён.")
    else:
        tour = event.text
        await event.answer("Запрос на добавление региона сохранён.")
    if tour is not None:
        data = await state.get_data()
        region = data.get("suggested_region_name")
        json_data = {"user_id": event.from_user.id, "region_name": region, "tour": tour if tour else None}
        put_data(json_data, "data/jsons/suggestions.json")
    await state.clear()