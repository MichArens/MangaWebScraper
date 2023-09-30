from typing import Any, Tuple
from pyppeteer.page import Page
from plugins.base_plugin_agent import BasePluginAgent
from utils.console_utils import start_choise_console


class MangaSearchService:
    def __init__(self) -> None:
        pass
    
    async def run(self, manga_name: str, page: Page, plugin: BasePluginAgent)-> Tuple[str, str]:
        names, hrefs = await plugin.search_for_manga(page, manga_name)
        item, index = start_choise_console("Pick a manga:", names)
        return item, hrefs[index]