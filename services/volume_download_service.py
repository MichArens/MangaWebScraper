import os
from typing import List
from pyppeteer import launch
from tqdm import tqdm
from plugins.base_plugin_agent import BasePluginAgent
from pyppeteer.page import Page

class VolumeChapterDownloadService:
    
    def __init__(self) -> None:
        self.pbar:tqdm = None
        self.pbar_desc = "Progress"
    
    async def run(self,page: Page, plugin: BasePluginAgent, manga_name: str, base_item_href: str, base_save_dir: str, items_to_download: List[int], is_volume: bool = False):
        prefix = "Volume" if is_volume else "Chapter"
        for item_number in items_to_download:
            item_url = await plugin.get_item_url(page, base_item_href, item_number, is_volume)
            self.pbar_desc = f"{prefix} {item_number}"
            await page.goto(item_url)
            save_dir = f"{base_save_dir}/{manga_name}/{prefix} {item_number}"
            os.makedirs(save_dir, exist_ok=True)
            await plugin.download_content(page, save_dir, self.__on_start, self.__on_progress, self.__on_error)
        
    def __on_start(self, total: int):
        self.pbar = tqdm(total=total, desc=self.pbar_desc)
        
    def __on_progress(self, progress_index: int):
        self.pbar.update(1)

    def __on_error(e: Exception):
        print(f"on_error {e}")