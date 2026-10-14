import re
from dataclasses import dataclass
from enum import StrEnum
from functools import lru_cache
from typing import Any

from src.utilities.database import markdown_store, region_rows, tour_rows

SLUG_RE = re.compile(r"[a-z0-9_]+")


class UnknownResourceError(LookupError):
    """Запрошен регион, маршрут или меню, которого нет в каталоге."""


@dataclass(frozen=True, slots=True)
class Tour:
    title: str
    slug: str
    pages: int
    map_links: dict[int, str]


@dataclass(frozen=True, slots=True)
class Region:
    title: str
    slug: str
    tours: tuple[Tour]


class MarkdownType(StrEnum):
    MENU = "menu"
    ABOUT_REGION = "about_region"
    TOUR = "tour"


def check_slug(slug: Any) -> None:
    """Проверяет, что slug соответствует допустимому формату.

    Args:
        slug(Any): Значение, которое нужно проверить.

    Raises:
        ValueError: Если значение не является строкой или содержит
            недопустимые символы.
    """
    if not isinstance(slug, str) or not SLUG_RE.fullmatch(slug):
        raise ValueError(f"Wrong slug format: {slug!r}")


@lru_cache
def get_regions() -> dict[str, Region]:
    """Собирает каталог регионов из таблиц regions и tours, загруженных при старте.

    Результат кэшируется: каталог меняется только после перезапуска бота.

    Returns:
        dict[str, Region]: Словарь slug региона -> Region в порядке position.

    Raises:
        ValueError: Если slug региона или маршрута имеет неверный формат.
    """
    tours_by_region: dict[int, list[Tour]] = {}
    for tour in tour_rows:
        check_slug(tour["slug"])
        map_links = {int(key): link for key, link in tour["map_links"].items()}
        tours_by_region.setdefault(tour["region_id"], []).append(
            Tour(title=tour["title"], slug=tour["slug"], pages=tour["pages"], map_links=map_links)
        )
    regions: dict[str, Region] = {}
    for row in region_rows:
        check_slug(row["slug"])
        regions[row["slug"]] = Region(
            row["title"], row["slug"], tuple(tours_by_region.get(row["id"], ()))
        )
    return regions


def get_region(slug: str | None) -> Region:
    """Возвращает регион по его slug.

    Args:
        slug(str | NOone): Уникальный идентификатор региона.

    Returns:
        Region: Найденный регион.

    Raises:
        UnknownResourceError: Если регион не найден или slug не указан.
    """
    region = get_regions().get(slug) if slug else None
    if region is None:
        raise UnknownResourceError(f"Unknown region: {slug!r}")
    return region


def get_tour(region_slug: str | None, tour_slug: str | None) -> Tour:
    """Находит маршрут в указанном регионе.

    Args:
        region_slug(str | None): Slug региона, которому принадлежит маршрут.
        tour_slug(str | None): Slug маршрута.

    Returns:
        Tour: Найденный маршрут.

    Raises:
        UnknownResourceError: Если регион или маршрут не найдены.
    """
    for tour in get_region(region_slug).tours:
        if tour.slug == tour_slug:
            return tour
    raise UnknownResourceError(f"Unknown tour {tour_slug!r} in region {region_slug!r}")


def get_tour_page_link(region_slug: str | None, tour_slug: str | None, page: int) -> str | None:
    """Возвращает ссылку на карту для указанной страницы маршрута.

    Args:
        region_slug(str | None): Slug региона.
        tour_slug(str | None): Slug маршрута.
        page(int): Номер страницы маршрута.

    Returns:
        str | None: URL карты или None, если для страницы ссылка не задана.

    Raises:
        UnknownResourceError: Если регион или маршрут не найдены.
    """
    tour = get_tour(region_slug, tour_slug)
    return tour.map_links.get(page)


def add_back_to_top_link(markdown: str, threshold: int) -> str:
    """Добавляет ссылку для возврата к началу длинной страницы.

    Args:
        markdown(str): Исходный текст в формате Markdown.
        threshold(int): Минимальная длина текста, при превышении которой
            добавляется ссылка.

    Returns:
        str: Исходный текст со ссылкой в начале и конце либо без изменений,
        если его длина не превышает threshold.
    """
    if len(markdown) > threshold:
        return '<a name="page-top"></a>\n' + markdown + "\n<br><br>[К началу страницы](#page-top)"
    return markdown


async def read_markdown(folder: str, name: str) -> str:
    """Возвращает текст страницы из загруженного при старте контента.

    Args:
        folder(str): Раздел контента: menus, about_region или tours.
        name(str): Имя страницы без расширения .md.

    Returns:
        str: Markdown страницы со ссылкой «К началу страницы» для длинных текстов.

    Raises:
        UnknownResourceError: Если такой страницы нет в базе.
    """
    content = markdown_store.get((folder, name))
    if content is None:
        raise UnknownResourceError(f"Markdown page not found: {folder}/{name}")
    return add_back_to_top_link(content, 700)


async def get_markdown(menu_type: MarkdownType, menu_name: str | None) -> str:
    """Возвращает Markdown-текст нужного раздела.

    Формирует имя файла в зависимости от типа контента и передаёт
    его в read_markdown для получения текста.

    Args:
        menu_type(MarkdownType): Тип контента: главное меню, описание региона
            или страница маршрута.
        menu_name(str): Название или slug региона, маршрута либо меню.

    Returns:
        str: Текст страницы в формате Markdown.

    Raises:
        UnknownResourceError: Если страница с указанным именем
            отсутствует в базе или тип контента не поддерживается.
    """
    match menu_type:
        case MarkdownType.MENU:
            return await read_markdown("menus", f"{menu_name}_menu")
        case MarkdownType.TOUR:
            return await read_markdown("tours", menu_name)
        case MarkdownType.ABOUT_REGION:
            return await read_markdown("about_region", f"about_{menu_name}")
        case _:
            raise UnknownResourceError(f"Unknown menu type: {menu_type!r}")
