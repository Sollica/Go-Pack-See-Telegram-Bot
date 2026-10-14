import logging

from aiogram import Router
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest
from aiogram.types import ErrorEvent, Message, Update

from src.utilities.load_data import UnknownResourceError

logger = logging.getLogger(__name__)
router = Router()

USER_ERROR_TEXT = "Что-то пошло не так. Попробуйте открыть главное меню: /main_menu"


async def notify_user(update: Update) -> None:
    """Отправляет пользователю сообщение об ошибке.

    Отправляет уведомление в чат, из которого поступило обновление.
    Если отправить сообщение не удалось, записывает предупреждение
    в журнал.

    Args:
        update (Update): Обновление Telegram, при обработке которого возникла ошибка.
    """
    try:
        if update.callback_query and isinstance(update.callback_query.message, Message):
            await update.callback_query.message.answer(USER_ERROR_TEXT)
        elif update.message:
            await update.message.answer(USER_ERROR_TEXT)
    except TelegramAPIError:
        logger.warning("User error notification failed", exc_info=True)


@router.errors()
async def on_error(event: ErrorEvent) -> bool:
    """Обрабатывает исключения, возникшие при обработке обновлений.

    Игнорирует ошибку неизменённого сообщения, отдельно регистрирует
    ошибки отсутствующих ресурсов и записывает остальные исключения.
    После этого пытается уведомить пользователя об ошибке.

    Args:
        event (ErrorEvent): Событие aiogram, содержащее исходное обновление
            и возникшее исключение.

    Returns:
        bool: True, чтобы сообщить aiogram, что ошибка обработана.
    """
    exc = event.exception

    if isinstance(exc, TelegramBadRequest) and "message is not modified" in str(exc):
        return True

    if isinstance(exc, UnknownResourceError):
        logger.warning("Unknown resource in update %s: %s", event.update.update_id, exc)
    else:
        logger.error("Unknown error in update %s", event.update.update_id, exc_info=exc)

    await notify_user(event.update)
    return True
