import logging
from collections.abc import Awaitable, Callable
from contextlib import suppress
from typing import Any

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.exceptions import TelegramAPIError
from aiogram.types import CallbackQuery, TelegramObject

logger = logging.getLogger(__name__)


class AnswerCallbackMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, CallbackQuery) and not get_flag(data, "manual_answer"):
            with suppress(TelegramAPIError):
                await event.answer()
        return await handler(event, data)
