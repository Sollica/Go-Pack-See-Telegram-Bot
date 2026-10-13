"""Работа с Supabase: загрузка контента при старте и запись отзывов пользователей."""
import asyncio
import logging
import os
from typing import Any

from supabase import AsyncClient, acreate_client

logger = logging.getLogger(__name__)

IMAGES_BUCKET = "images"

markdown_store: dict[tuple[str, str], str] = {}
"""Тексты меню и маршрутов: (папка, имя файла без .md) -> Markdown."""

image_store: dict[str, bytes] = {}
"""Картинки из хранилища Supabase: имя файла -> содержимое."""

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
    """Загружает каталог регионов, все тексты и картинки из Supabase в память.

    Вызывается один раз перед запуском бота. Если загрузить контент не удалось,
    бот не должен запускаться.

    Raises:
        ContentLoadError: Если база недоступна или таблица регионов или текстов пуста.
    """
    try:
        client = await get_client()
        regions = (await client.table("regions").select("*").order("position").execute()).data
        tours = (await client.table("tours").select("*").order("position").execute()).data
        response = await client.table("markdown").select("kind,name,content").execute()
        rows: list[dict[str, Any]] = response.data
        bucket = client.storage.from_(IMAGES_BUCKET)
        files = await bucket.list("", {"limit": 1000})
        names = [f["name"] for f in files if not f["name"].startswith(".")]
        contents = await asyncio.gather(*(bucket.download(name) for name in names))
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
    image_store.update(dict(zip(names, contents)))
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
