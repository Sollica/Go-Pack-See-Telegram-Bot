import json
import os

import aiofiles


def load_data(path: str):
    with open(path) as f:
        return json.load(f)

def put_data(data: dict, path: str):
    if not os.path.exists(path) or os.stat(path).st_size == 0:
        with open(path, "w") as file:
            json.dump([], file)
    with open(path, "r") as file:
        file_data = json.load(file)
    file_data.append(data)
    with open(path, "w") as file:
        json.dump(file_data, file, indent=4, ensure_ascii=False)
    

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