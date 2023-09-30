import os
from typing import List
from pyppeteer import launch
from tqdm import tqdm
from plugins.base_plugin_agent import BasePluginAgent
from pyppeteer.page import Page

class VolumeChapterDownloadService:
    
    def __init__(self) -> None:
        self.pbar:tqdm = None
    
    async def run(self,page: Page, plugin: BasePluginAgent, manga_name: str, base_item_href: str, base_save_dir: str, items_to_download: List[int], is_volume: bool = False):
        prefix = "Volume" if is_volume else "Chapter"
        for item_number in items_to_download:
            item_url = f"{self.__get_plain_href(base_item_href)}/{prefix.lower()}-{item_number}"
            print("going to ", item_url)
            await page.goto(item_url)
            save_dir = f"{base_save_dir}/{manga_name}/{prefix} {item_number}"
            os.makedirs(save_dir, exist_ok=True)
            await plugin.download_content(page, save_dir, self.__on_start, self.__on_progress, self.__on_error)
        
    def __on_start(self, total: int):
        self.pbar = tqdm(total=total, desc="Progress")
        
    def __on_progress(self, progress_index: int):
        self.pbar.update(1)

    def __on_error(e: Exception):
        print(f"on_error {e}")
    
    #TODO maybe move to agent plugin
    def __get_plain_href(self, base_href: str):
        char_to_find = '/'

        # Use rfind() to get the index of the last occurrence of the character
        last_index = base_href.rfind(char_to_find)

        if last_index != -1:
            # Extract a substring from the start to a specific index (exclusive)
            index_to_extract_to = last_index
            substring = base_href[:index_to_extract_to]

            return substring
        
        raise Exception("Bad url")