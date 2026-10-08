import json
import re
from dataclasses import dataclass
from enum import StrEnum
from functools import lru_cache
from pathlib import Path
from typing import Any

import aiofiles

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
JSONS_DIR = DATA_DIR / "jsons"
MARKDOWN_DIR = DATA_DIR / "markdown"

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


def load_data(path: Path | str) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def check_slug(slug: Any) -> None:
    if not isinstance(slug, str) or not SLUG_RE.fullmatch(slug):
        raise ValueError(f"Wrong slug format: {slug!r}")


@lru_cache
def get_regions() -> dict[str, Region]:
    raw = load_data(JSONS_DIR / "regions.json")
    regions: dict[str, Region] = {}
    for region_slug, region_data in raw.items():
        check_slug(region_slug)
        tours = []
        for tour in region_data["tours"]:
            check_slug(tour["slug"])
            map_links = {int(key): link for key, link in tour["map_links"].items()}
            tours.append(Tour(
                title=tour["title"],
                slug=tour["slug"],
                pages=tour["pages"],
                map_links=map_links))
        regions[region_slug] = Region(region_data["title"], region_slug, tuple(tours))
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


async def read_markdown(folder: str, filename: str) -> str:
    base = (MARKDOWN_DIR / folder).resolve()
    path = (base / filename).resolve()
    try:
        async with aiofiles.open(path, encoding="utf-8") as f:
            return add_back_to_top_link(await f.read(), 700)
    except FileNotFoundError as exc:
        raise UnknownResourceError(f"Markdown file not found: {path.name}") from exc


async def get_markdown(menu_type: MarkdownType, menu_name: str | None) -> str:
    match menu_type:
        case MarkdownType.MENU:
            return await read_markdown("menus", f"{menu_name}_menu.md")
        case MarkdownType.TOUR:
            return await read_markdown("tours", f"{menu_name}.md")
        case MarkdownType.ABOUT_REGION:
            return await read_markdown("about_region", f"about_{menu_name}.md")
        case _:
            raise UnknownResourceError(f"Unknown menu type: {menu_type!r}")
