import json

import aiofiles


def load_data(path: str):
    with open(path) as f:
        return json.load(f)
    

class GetMarkdown:
    @staticmethod
    async def menu_markdown(menu: str | None) -> str:
        async with aiofiles.open(f"data/markdown/menus/{menu}_menu.md") as f:
            return await f.read()

    @staticmethod
    async def tour_markdown(tour: str | None) -> str:
        async with aiofiles.open(f"data/markdown/tours/{tour}_tour.md") as f:
            return await f.read()

    @staticmethod
    async def about_region_markdown(region: str | None) -> str:
        async with aiofiles.open(f"data/markdown/about_region/about_{region}.md") as f:
            return await f.read()