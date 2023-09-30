from typing import Any
from pyppeteer.page import Page
from plugins.mangareader import MangaReader
from utils.console_utils import start_choise_console


class MangaSearchService:
    def __init__(self) -> None:
        pass
    
    async def run(self, manga_name: str, page: Page, plugin: Any):
        names, hrefs = await plugin.search_for_manga(page, manga_name)
        item, index = start_choise_console("Pick a manga:", names)
        print(names[index], hrefs[index])
        return hrefs[index]