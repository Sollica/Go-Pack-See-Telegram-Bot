import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from src.handlers import command_handlers, error_handlers, navigation_handlers
from src.middlewares import AnswerCallbackMiddleware, LocalImagesMiddleware
from src.utilities.database import ContentLoadError, load_content

logger = logging.getLogger(__name__)


def build_dispatcher() -> Dispatcher:
    """Создаёт и настраивает диспетчер бота.

    Регистрирует middleware для обработки callback-запросов
    и подключает маршрутизаторы для обработки ошибок, навигации
    и команд пользователя.

    Returns:
        Dispatcher: Настроенный диспетчер с зарегистрированными
            маршрутизаторами и middleware.
    """
    dp = Dispatcher()
    dp.callback_query.middleware(AnswerCallbackMiddleware())
    for router in (
        error_handlers.router,
        navigation_handlers.router,
        command_handlers.router,
    ):
        dp.include_router(router)
    return dp


async def main() -> None:
    """Инициализирует и запускает Telegram-бота.

    Загружает переменные окружения, проверяет наличие токена бота,
    загружает содержимое из базы данных, настраивает middleware
    сессии и запускает обработку входящих обновлений.

    Raises:
        SystemExit: Если токен бота не задан или произошла ошибка
            при загрузке содержимого.
    """
    load_dotenv()
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise SystemExit("BOT_TOKEN not set")

    try:
        await load_content()
    except ContentLoadError as exc:
        raise SystemExit(f"Бот не запущен: {exc}") from exc

    bot = Bot(token=token)
    bot.session.middleware(LocalImagesMiddleware())
    dp = build_dispatcher()

    logger.info("Bot is starting")
    await dp.start_polling(bot)


def run() -> None:
    """Настраивает логи и запускает бота.

    Запускает асинхронную функцию main() в цикле событий
    и обрабатывает штатное завершение работы по прерыванию
    пользователем.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped")


if __name__ == "__main__":
    run()
