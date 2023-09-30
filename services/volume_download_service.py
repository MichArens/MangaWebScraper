from pyppeteer import launch
from tqdm import tqdm
from plugins.base_plugin_agent import BasePluginAgent
from pyppeteer.page import Page

class VolumeDownloadService:
    
    def __init__(self) -> None:
        self.pbar:tqdm = None
    
    async def run(self, url: str, save_dir: str, page: Page, plugin: BasePluginAgent):
        await page.goto(url)
        await plugin.download_content(page, save_dir, self.__on_start, self.__on_progress, self.__on_error)
        
    def __on_start(self, total: int):
        self.pbar = tqdm(total=total, desc="Progress")
        
    def __on_progress(self, progress_index: int):
        self.pbar.update(1)

    def __on_error(e: Exception):
        print(f"on_error {e}")