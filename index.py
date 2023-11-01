import asyncio
import os
import argparse
    
from pyppeteer import launch
from plugins.base_plugin_agent import BasePluginAgent
from plugins.mangareader import MangaReader
from services.manga_search_service import MangaSearchService
from services.volume_chapter_pick_service import VolumeChapterPickService
from services.volume_download_service import VolumeChapterDownloadService

def handle_args():
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="A script with required and optional command-line arguments")

    # Define a required argument
    parser.add_argument("--save_dir", help="The directory to save the manga", type=str, required=True)

    # Define an optional argument
    parser.add_argument("--manga_name", help="The name of the manga to download", type=str, required=True)
    
    parser.add_argument("--manga_url", help="The url of the manga to download (Will skip manga search) (Optional)", type=str)
    
    parser.add_argument("--download_amount", help="The amount of volumes/chaters that will be downloaded (Example - All / 1 / 2-3 / 1,3-5,7-9) (Optional)", type=str)

    # Parse the command-line arguments
    args = parser.parse_args()

    return args.save_dir, args.manga_name, args.manga_url, args.download_amount
    
def get_plugin(plugin_id: str)-> BasePluginAgent:
    return MangaReader()

async def main(manga_name: str, save_dir: str, manga_url: str = None, download_amount: str = None):
    browser = await launch(headless=True)
    try:
        page = await browser.newPage()
        
        #First launch
        plugin = get_plugin("manga_reader")
        await page.goto(plugin.home_url)
        await plugin.clear_first_popup(page)
        
        manga_name = manga_name
        href = manga_url
        if manga_url is None:
            #Manga searching service
            mss = MangaSearchService()
            manga_name, href = await mss.run(manga_name, page, plugin)
            print("You picked:", manga_name, href)
        
        #Volume/Chapter picking service
        vcps = VolumeChapterPickService()
        is_volume: bool = True #TODO get from run
        number_of_items, item_example_href = await vcps.run(page, plugin, href, is_volume)
        items_to_download = vcps.pick_chapters_or_volumes(number_of_items, is_volume, download_amount)
        
        #Volume/Chatper download service
        vcds = VolumeChapterDownloadService()
        await vcds.run(page, plugin, manga_name, item_example_href, save_dir, items_to_download, is_volume)
    except Exception as e:
        print(e)
        await browser.close()
    
if __name__ == '__main__':
    save_dir, manga_name, manga_url, download_amount = handle_args()
    os.makedirs(save_dir, exist_ok=True)
    asyncio.get_event_loop().run_until_complete(main(manga_name, save_dir, manga_url, download_amount))