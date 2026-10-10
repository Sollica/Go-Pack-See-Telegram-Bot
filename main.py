import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from handlers import command_handlers, error_handlers, navigation_handlers
from middlewares import AnswerCallbackMiddleware, LocalImagesMiddleware

logger = logging.getLogger(__name__)


def build_dispatcher() -> Dispatcher:
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
    load_dotenv()
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise SystemExit("BOT_TOKEN not set")

    bot = Bot(token=token)
    bot.session.middleware(LocalImagesMiddleware())
    dp = build_dispatcher()

    logger.info("Bot is starting")
    await dp.start_polling(bot)


def run() -> None:
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
