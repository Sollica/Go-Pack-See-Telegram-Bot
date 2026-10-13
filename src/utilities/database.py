"""Работа с Supabase: загрузка контента при старте и запись отзывов пользователей."""
import asyncio
import logging
import os
from typing import Any

from supabase import AsyncClient, acreate_client

logger = logging.getLogger(__name__)

IMAGES_BUCKET = "images"
SIGNED_URL_TTL = 365 * 24 * 60 * 60
"""Срок жизни ссылок на картинки, в секундах (год)."""

markdown_store: dict[tuple[str, str], str] = {}
"""Тексты меню и маршрутов: (папка, имя файла без .md) -> Markdown."""

image_store: dict[str, str] = {}
"""Картинки из хранилища Supabase: имя файла -> подписанная ссылка на файл."""

region_rows: list[dict[str, Any]] = []
"""Строки таблицы regions, отсортированные по position."""

tour_rows: list[dict[str, Any]] = []
"""Строки таблицы tours, отсортированные по position."""

_client: AsyncClient | None = None


class ContentLoadError(RuntimeError):
    """Не удалось загрузить контент из базы данных."""


async def get_client() -> AsyncClient:
    """Возвращает общий асинхронный клиент Supabase, создавая его при первом вызове.

    Returns:
        Клиент Supabase.

    Raises:
        ContentLoadError: Если в окружении нет SUPABASE_URL или SUPABASE_KEY.
    """
    global _client
    if _client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise ContentLoadError("SUPABASE_URL или SUPABASE_KEY не заданы в .env")
        _client = await acreate_client(url, key)
    return _client


async def load_content() -> None:
    """Загружает каталог регионов, все тексты и ссылки на картинки из Supabase в память.

    Сами картинки не скачиваются: для каждой одним запросом получается подписанная
    ссылка, по которой файл при первом показе забирает Telegram.

    Вызывается один раз перед запуском бота. Если загрузить контент не удалось,
    бот не должен запускаться.

    Raises:
        ContentLoadError: Если база недоступна или таблица регионов или текстов пуста.
    """
    try:
        client = await get_client()
        bucket = client.storage.from_(IMAGES_BUCKET)
        regions_resp, tours_resp, markdown_resp, files = await asyncio.gather(
            client.table("regions").select("*").order("position").execute(),
            client.table("tours").select("*").order("position").execute(),
            client.table("markdown").select("kind,name,content").execute(),
            bucket.list("", {"limit": 1000}),
        )
        regions: list[dict[str, Any]] = regions_resp.data
        tours: list[dict[str, Any]] = tours_resp.data
        rows: list[dict[str, Any]] = markdown_resp.data
        names = [f["name"] for f in files if not f["name"].startswith(".")]
        signed = await bucket.create_signed_urls(names, SIGNED_URL_TTL) if names else []
    except ContentLoadError:
        raise
    except Exception as exc:
        raise ContentLoadError(f"Не удалось загрузить контент из Supabase: {exc}") from exc

    if not regions:
        raise ContentLoadError("Таблица regions пуста")
    if not rows:
        raise ContentLoadError("Таблица markdown пуста")

    region_rows[:] = regions
    tour_rows[:] = tours

    markdown_store.clear()
    markdown_store.update({(row["kind"], row["name"]): row["content"] for row in rows})
    image_store.clear()
    image_store.update({item["path"]: item["signedURL"] for item in signed if item["signedURL"]})
    logger.info(
        "Loaded %d regions, %d tours, %d markdown pages and %d images",
        len(region_rows), len(tour_rows), len(markdown_store), len(image_store),
    )


async def insert_row(table: str, record: dict[str, Any]) -> None:
    """Добавляет одну запись в таблицу Supabase.

    Args:
        table: Имя таблицы.
        record: Значения полей новой записи.
    """
    client = await get_client()
    await client.table(table).insert(record).execute()
