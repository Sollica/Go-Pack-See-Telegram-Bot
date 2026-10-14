import logging

from src.utilities.database import insert_row

logger = logging.getLogger(__name__)


async def save_suggestion(
    user_id: int, username: str | None, region_name: str | None, tour: str | None
) -> None:
    """Сохраняет предложение нового региона или маршрута в таблицу suggestions.

    Args:
        user_id(int): ID пользователя Telegram.
        usernamestr | None: Username пользователя, если есть.
        region_namestr | None: Предложенный регион.
        tourstr | None: Предложенный маршрут, если пользователь его указал.
    """
    await insert_row(
        "suggestions",
        {
            "user_id": user_id,
            "username": username,
            "region_name": region_name,
            "tour": tour or None,
        },
    )


async def save_bug_report(user_id: int, username: str | None, report: str | None) -> None:
    """Сохраняет сообщение об ошибке в таблицу bug_reports.

    Args:
        user_id(int): ID пользователя Telegram.
        username(str | None): Username пользователя, если есть.
        report(str | None): Текст сообщения об ошибке.
    """
    await insert_row("bug_reports", {"user_id": user_id, "username": username, "report": report})
