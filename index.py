import asyncio
import os
import argparse
    
from pyppeteer import launch
from enums.args_enum import ARGS_ENUM
from plugins.base_plugin_agent import BasePluginAgent
from plugins.mangareader import MangaReader
from services.manga_search_service import MangaSearchService
from services.volume_chapter_pick_service import VolumeChapterPickService
from services.volume_download_service import VolumeChapterDownloadService

def handle_args():
    parser = argparse.ArgumentParser(description="A script with required and optional command-line arguments")
    required_args = []
    for arg in ARGS_ENUM:
        parser.add_argument(arg.value.runName, help=arg.value.help, type=arg.value.type, default=arg.value.get_default())
        if arg.value.required is True:
            required_args.append(arg.value.runName.removeprefix('--'))
    args_var = vars(parser.parse_args())
    
    missing_args = []
    for arg in required_args:
        if args_var[arg] is None:
            missing_args.append(arg)
            
    if len(missing_args) > 0:
        print(f'{["--{}".format(item) for item in missing_args]} arguments are required and missing from run command.\nPlease run "index.py --help" for more information.')
        return None
    
    return args_var
            
    
def get_plugin(plugin_id: str)-> BasePluginAgent:
    #TODO: enum with switch case for more agents
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
    args = handle_args()
    if args is not None:
        save_dir = args['save_dir']
        manga_name = args['manga_name']
        manga_url = args['manga_url']
        download_amount = args['download_amount']
        os.makedirs(save_dir, exist_ok=True)
        asyncio.get_event_loop().run_until_complete(main(manga_name, save_dir, manga_url, download_amount))