from pyppeteer import launch
from tqdm import tqdm

from plugins.mangareader import MangaReader

class VolumeDownloadService:
    
    def __init__(self) -> None:
        self.pbar:tqdm = None
    
    async def run(self, url: str, save_dir: str):
        browser = await launch(headless=True)
        page = await browser.newPage()
        await page.goto(url)
        manga_reader = MangaReader()
        
        await manga_reader.pass_first(page)
        await manga_reader.download_content(page, save_dir, self.__on_start, self.__on_progress, self.__on_error)
        browser.close()
        
    def __on_start(self, total: int):
        self.pbar = tqdm(total=total, desc="Progress")
        
    def __on_progress(self, progress_index: int):
        # print(f"on_progress {progress_index}")
        self.pbar.update(1)

    def __on_error(e: Exception):
        print(f"on_error {e}")