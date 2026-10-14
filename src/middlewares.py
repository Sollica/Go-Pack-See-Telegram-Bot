import logging
import random
import re
from collections.abc import Awaitable, Callable
from contextlib import suppress
from fnmatch import fnmatch
from typing import Any

from aiogram import BaseMiddleware, Bot
from aiogram.client.session.middlewares.base import BaseRequestMiddleware, NextRequestMiddlewareType
from aiogram.dispatcher.flags import get_flag
from aiogram.exceptions import TelegramAPIError
from aiogram.methods import EditMessageText, SendRichMessage, TelegramMethod
from aiogram.methods.base import TelegramType
from aiogram.types import (
    CallbackQuery,
    InputMediaPhoto,
    InputRichMessage,
    InputRichMessageMedia,
    Message,
    RichBlockPhoto,
    TelegramObject,
)

from src.utilities.database import image_store

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


LOCAL_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(local:([^)\s]+)\)")


class LocalImagesMiddleware(BaseRequestMiddleware):
    """Подставляет в rich-сообщения картинки из хранилища Supabase по ссылкам ``local:имя_файла``.

    Имя может быть шаблоном со звёздочкой (``local:main_menu_*.jpg``): тогда при каждом
    показе выбирается случайный подходящий файл. При первом показе файл загружается
    в Telegram, затем используется сохранённый file_id.
    """

    def __init__(self) -> None:
        self.file_ids: dict[str, str] = {}

    async def __call__(
        self,
        make_request: NextRequestMiddlewareType[TelegramType],
        bot: Bot,
        method: TelegramMethod[TelegramType],
    ) -> TelegramType:
        """Заменяет локальные картинки в исходящем запросе и запоминает их file_id.

        Args:
            make_request: Следующий обработчик запроса.
            bot: Экземпляр бота.
            method: Отправляемый метод Telegram API.

        Returns:
            Результат запроса (сообщение).

        Raises:
            FileNotFoundError: Если указанной картинки нет в хранилище.
        """
        rich = getattr(method, "rich_message", None)
        if not (
            isinstance(method, (SendRichMessage, EditMessageText))
            and isinstance(rich, InputRichMessage)
            and rich.markdown
            and "local:" in rich.markdown
        ):
            return await make_request(bot, method)

        filenames: list[str] = []
        media: list[InputRichMessageMedia] = []

        def replace(match: re.Match[str]) -> str:
            caption, filename = match.groups()
            if "*" in filename:
                candidates = sorted(name for name in image_store if fnmatch(name, filename))
                if not candidates:
                    raise FileNotFoundError(f"No images match: {filename}")
                filename = random.choice(candidates)
            url = image_store.get(filename)
            if url is None:
                raise FileNotFoundError(f"Image not found: {filename}")
            media_id = f"img{len(media) + 1}"
            source = self.file_ids.get(filename) or url
            media.append(InputRichMessageMedia(id=media_id, media=InputMediaPhoto(media=source)))
            filenames.append(filename)
            return f"![{caption}](tg://photo?id={media_id})"

        markdown = LOCAL_IMAGE_RE.sub(replace, rich.markdown)
        method.rich_message = rich.model_copy(update={"markdown": markdown, "media": media})
        result = await make_request(bot, method)
        self._remember_file_ids(result, filenames)
        return result

    def _remember_file_ids(self, result: Any, filenames: list[str]) -> None:
        """Запоминает file_id загруженных картинок из ответа Telegram.

        Ошибки здесь не пробрасываются: сообщение уже отправлено, а без file_id
        картинка просто загрузится заново в следующий раз.

        Args:
            result: Результат запроса (обычно отправленное или изменённое сообщение).
            filenames: Имена локальных файлов в порядке появления в сообщении.
        """
        message = getattr(result, "result", result)
        if not isinstance(message, Message) or message.rich_message is None:
            return
        try:
            photos = [block for block in message.rich_message.blocks if isinstance(block, RichBlockPhoto)]
            if len(photos) != len(filenames):
                return
            for filename, block in zip(filenames, photos):
                self.file_ids.setdefault(filename, block.photo[-1].file_id)
        except Exception:
            logger.warning("Не удалось сохранить file_id для %s", filenames, exc_info=True)
