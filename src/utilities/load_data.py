import re
from dataclasses import dataclass
from enum import StrEnum
from functools import lru_cache
from typing import Any

from utilities.database import markdown_store, region_rows, tour_rows


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
    if not isinstance(slug, str) or not SLUG_RE.fullmatch(slug):
        raise ValueError(f"Wrong slug format: {slug!r}")


@lru_cache
def get_regions() -> dict[str, Region]:
    """Собирает каталог регионов из таблиц regions и tours, загруженных при старте.

    Результат кэшируется: каталог меняется только после перезапуска бота.

    Returns:
        Словарь slug региона -> Region в порядке position.

    Raises:
        ValueError: Если slug региона или маршрута имеет неверный формат.
    """
    tours_by_region: dict[int, list[Tour]] = {}
    for tour in tour_rows:
        check_slug(tour["slug"])
        map_links = {int(key): link for key, link in tour["map_links"].items()}
        tours_by_region.setdefault(tour["region_id"], []).append(Tour(
            title=tour["title"],
            slug=tour["slug"],
            pages=tour["pages"],
            map_links=map_links))
    regions: dict[str, Region] = {}
    for row in region_rows:
        check_slug(row["slug"])
        regions[row["slug"]] = Region(
            row["title"], row["slug"], tuple(tours_by_region.get(row["id"], ())))
    return regions


def get_region(slug: str | None) -> Region:
    region = get_regions().get(slug) if slug else None
    if region is None:
        raise UnknownResourceError(f"Unknown region: {slug!r}")
    return region


def get_tour(region_slug: str | None, tour_slug: str | None) -> Tour:
    for tour in get_region(region_slug).tours:
        if tour.slug == tour_slug:
            return tour
    raise UnknownResourceError(f"Unknown tour {tour_slug!r} in region {region_slug!r}")


def get_tour_page_link(region_slug: str | None, tour_slug: str | None, page: int) -> str | None:
    tour = get_tour(region_slug, tour_slug)
    return tour.map_links.get(page)


def add_back_to_top_link(markdown: str, threshold: int) -> str:
    if len(markdown) > threshold:
        return '<a name="page-top"></a>\n' + markdown + "\n<br><br>[К началу страницы](#page-top)"
    return markdown


async def read_markdown(folder: str, name: str) -> str:
    """Возвращает текст страницы из загруженного при старте контента.

    Args:
        folder: Раздел контента: menus, about_region или tours.
        name: Имя страницы без расширения .md.

    Returns:
        Markdown страницы со ссылкой «К началу страницы» для длинных текстов.

    Raises:
        UnknownResourceError: Если такой страницы нет в базе.
    """
    content = markdown_store.get((folder, name))
    if content is None:
        raise UnknownResourceError(f"Markdown page not found: {folder}/{name}")
    return add_back_to_top_link(content, 700)


async def get_markdown(menu_type: MarkdownType, menu_name: str | None) -> str:
    match menu_type:
        case MarkdownType.MENU:
            return await read_markdown("menus", f"{menu_name}_menu")
        case MarkdownType.TOUR:
            return await read_markdown("tours", menu_name)
        case MarkdownType.ABOUT_REGION:
            return await read_markdown("about_region", f"about_{menu_name}")
        case _:
            raise UnknownResourceError(f"Unknown menu type: {menu_type!r}")
