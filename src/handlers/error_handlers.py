import logging

from aiogram import Router
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest
from aiogram.types import ErrorEvent, Message, Update

from utilities.load_data import UnknownResourceError

logger = logging.getLogger(__name__)
router = Router()

USER_ERROR_TEXT = "Что-то пошло не так. Попробуйте открыть главное меню: /main_menu"


async def notify_user(update: Update) -> None:
    try:
        if update.callback_query and isinstance(update.callback_query.message, Message):
            await update.callback_query.message.answer(USER_ERROR_TEXT)
        elif update.message:
            await update.message.answer(USER_ERROR_TEXT)
    except TelegramAPIError:
        logger.warning("User error notification failed", exc_info=True)


@router.errors()
async def on_error(event: ErrorEvent) -> bool:
    exc = event.exception

    if isinstance(exc, TelegramBadRequest) and "message is not modified" in str(exc):
        return True

    if isinstance(exc, UnknownResourceError):
        logger.warning("Unknown resource in update %s: %s", event.update.update_id, exc)
    else:
        logger.error("Unknown error in update %s", event.update.update_id, exc_info=exc)

    await notify_user(event.update)
    return True
