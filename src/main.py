import asyncio
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from handlers import command_handlers, menu_handlers, region_menu_handlers

load_dotenv()
token = os.getenv("BOT_TOKEN")
if token is None:
    raise Exception("BOT_TOKEN environment variable not found")  # noqa: TRY002

bot = Bot(token=token)
dp = Dispatcher()

routers = [
    menu_handlers.router,
    region_menu_handlers.router,
    command_handlers.router
]

async def main():
    for router in routers:
        dp.include_router(router)

    print(
        "==============\n"
        "BOT IS RUNNING\n"
        "=============="
    )

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())