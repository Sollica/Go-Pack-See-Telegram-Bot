import logging

from aiogram import Router, types
from aiogram.enums import ParseMode
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InputRichMessage, Message

from src.data.forms import Form
from src.keyboards.navigation_keyboards import cancel_keyboard, main_menu_keyboard, skip_keyboard
from src.utilities.load_data import MarkdownType, get_markdown
from src.utilities.save_data import save_bug_report, save_suggestion

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    """Обрабатывает команду /start и приветствует пользователя.

    Отправляет приветственное сообщение и открывает главное меню.

    Args:
        message (types.Message): Сообщение пользователя с командой /start.
        state (FSMContext): Контекст конечного автомата пользователя.
    """
    await message.answer(
        (
            "Добро пожаловать в *_Go, Pack & See\\!_*\n\n"
            ""
            "Используйте встроенную клавиатуру для навигации "
            "по меню и изучайте регионы России с нами\\!"
        ),
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    await main_menu(message, state)


@router.message(Command("main_menu"))
async def main_menu(message: types.Message, state: FSMContext):
    """Открывает главное меню бота.

    Сбрасывает текущее состояние пользователя и отправляет
    содержимое главного меню с клавиатурой навигации.

    Args:
        message (types.Message): Сообщение пользователя с командой /main_menu.
        state( FSMContext): Контекст конечного автомата пользователя.
    """
    await state.clear()
    await message.answer_rich(
        InputRichMessage(markdown=await get_markdown(MarkdownType.MENU, "main")),
        reply_markup=main_menu_keyboard(),
    )


@router.message(Command("suggest"))
async def suggest(message: types.Message, state: FSMContext):
    """Начинает процесс предложения нового региона.

    Просит пользователя указать название региона и переводит
    диалог в состояние ожидания названия.

    Args:
        message (types.Message): Сообщение пользователя с командой /suggest.
        state (FSMContext): Контекст конечного автомата пользователя.
    """
    await message.answer(
        (
            "Хотите увидеть новый регион в нашем проекте? "
            "Поделитесь своими пожеланиями с нами!\n\n"
            "Напишите название региона, который нам стоит добавить в проект."
        ),
        reply_markup=cancel_keyboard,
    )
    await state.set_state(Form.suggest_region_name)


@router.message(Form.suggest_region_name)
@router.callback_query(Form.suggest_region_name)
async def suggest_region(event: Message | CallbackQuery, state: FSMContext):
    """Обрабатывает название предлагаемого региона или отмену.

    При получении сообщения сохраняет название региона во временном
    состоянии и предлагает пользователю описать маршрут.
    При получении callback-запроса отменяет предложение.

    Args:
        event (Message | CallbackQuery): Сообщение пользователя или callback-запрос от кнопки.
        state (FSMContext): Контекст конечного автомата пользователя.
    """
    if isinstance(event, CallbackQuery):
        await event.message.edit_text("Запрос на добавление региона отменён.")
        await state.clear()
    else:
        await state.update_data(suggested_region_name=event.text)
        await event.answer(
            (
                f"Если у вас есть идеи насчёт конкретного маршрута "
                f"для региона «{event.text}», пожалуйста, напишите их ниже."
            ),
            reply_markup=skip_keyboard,
        )
        await state.set_state(Form.suggest_tour)


@router.message(Form.suggest_tour)
@router.callback_query(Form.suggest_tour)
async def suggest_tour(event: Message | CallbackQuery, state: FSMContext):
    """Обрабатывает описание маршрута для предлагаемого региона.

    Позволяет пользователю описать маршрут, пропустить этот шаг
    или отменить предложение. Если предложение не отменено,
    сохраняет название региона и описание маршрута.

    Args:
        event (Message | CallbackQuery): Сообщение пользователя или callback-запрос от кнопки.
        state (FSMContext): Контекст конечного автомата пользователя.
    """
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
        await save_suggestion(
            user_id=event.from_user.id,
            username=event.from_user.username,
            region_name=data.get("suggested_region_name"),
            tour=tour,
        )
        logger.info(
            f"User {event.from_user.username} (user_id: {event.from_user.id}) has suggested a region."
        )
    await state.clear()


@router.message(Command("bug_report"))
async def bug_report_start(message: types.Message, state: FSMContext):
    """Начинает процесс отправки отчёта об ошибке.

    Просит пользователя описать обнаруженную проблему и переводит
    диалог в состояние ожидания отчёта.

    Args:
        message (types.Message): Сообщение пользователя с командой /bug_report.
        state (FSMContext): Контекст конечного автомата пользователя.
    """
    await message.answer(
        (
            "Столкнулись с ошибкой в работе бота?\n\n"
            "Пожалуйста, опишите проблему, с которой вы столкнулись, "
            "и мы постараемся её исправить!"
        ),
        reply_markup=cancel_keyboard,
    )
    await state.set_state(Form.bug_report)


@router.message(Form.bug_report)
@router.callback_query(Form.bug_report)
async def process_bug_report(event: Message | CallbackQuery, state: FSMContext):
    """Обрабатывает отправку или отмену отчёта об ошибке.

    При получении сообщения сохраняет отчёт и записывает событие
    в журнал. При получении callback-запроса отменяет отправку.
    После обработки очищает состояние пользователя.

    Args:
        event (Message | CallbackQuery): Сообщение пользователя или callback-запрос от кнопки.
        state (FSMContext): Контекст конечного автомата пользователя.
    """
    if isinstance(event, CallbackQuery):
        await event.message.edit_text("Отправка отчёта об ошибке отменена.")
    else:
        await save_bug_report(
            user_id=event.from_user.id, username=event.from_user.username, report=event.text
        )
        await event.answer("Спасибо за информацию! Мы уже работаем над исправлением.")
        logger.info(
            f"User {event.from_user.username} (user_id: {event.from_user.id}) has reported a bug."
        )

    await state.clear()
