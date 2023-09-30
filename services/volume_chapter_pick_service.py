from typing import Any, List, Tuple
from pyppeteer.page import Page
from plugins.base_plugin_agent import BasePluginAgent

class VolumeChapterPickService:
    def __init__(self) -> None:
        pass
    
    async def run(self, page: Page, plugin: BasePluginAgent, manga_href: str, volume_mode: bool = False)-> Tuple[str, str]:
        await page.goto(manga_href)
        number_of_items = await plugin.get_chapters_or_volumes(page, volume_mode)
        return number_of_items
    
    def pick_chapters_or_volumes(self, number_of_items: int = 1, is_volume: bool = False)->List[int]:
        item_name = 'Volumes' if is_volume else 'Chapters'
        choice = input(f"Detected {number_of_items} {item_name}, please select the {item_name} you want to download: (Example - All / 1 / 2-3 / 1,3-5,7-9 \n")
        
        items_to_download = []
        
        if choice == "All":
            items_to_download = [i for i in range(1, number_of_items + 1)]
            return items_to_download
        
        choice = choice.replace(" ", "")
        unpack_choice: List[str] = choice.split(",")
        for single_choice in unpack_choice:
            if "-" in single_choice:
                range_items = single_choice.split("-")
                range_list = [i for i in range(int(range_items[0]), int(range_items[1]) + 1)]
                items_to_download += range_list
            else:
                items_to_download.append(int(single_choice))
                
        return items_to_download