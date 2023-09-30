import asyncio
import os

from pyppeteer import launch
from plugins.base_plugin_agent import BasePluginAgent
from plugins.mangareader import MangaReader
from services.manga_search_service import MangaSearchService
from services.volume_download_service import VolumeDownloadService

def get_plugin(plugin_id: str)-> BasePluginAgent:
    return MangaReader()

async def main(manga_name: str):
    browser = await launch(headless=True)
    page = await browser.newPage()
    plugin = get_plugin("manga_reader")
    await page.goto(plugin.home_url)
    await plugin.clear_first_popup(page)
    
    mss = MangaSearchService()
    name, href = await mss.run(manga_name, page, plugin)
    print("You picked:", name, href)
    await browser.close()
    
if __name__ == '__main__':
    url = 'https://mangareader.to/read/ge-good-ending-1056/en/volume-1'  # Replace with the URL of the website
    save_dir = "downloaded_images"
    os.makedirs(save_dir, exist_ok=True)
    asyncio.get_event_loop().run_until_complete(main("ge good ending"))
    # vds = VolumeDownloadService()
    # asyncio.get_event_loop().run_until_complete(vds.run(url, save_dir))