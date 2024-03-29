import asyncio
import base64
from types import FunctionType
from typing import List
from pyppeteer.page import Page
import requests

from plugins.base_plugin_agent import BasePluginAgent
from utils.generic_utils import get_href_no_last_part

class MangaReader(BasePluginAgent):
    
    def __init__(self):
        self.home_url = "https://mangareader.to/"
    
    async def clear_first_popup(self, page: Page, retries: int = 10):
        await page.waitForSelector("#st-cmp-v2 > div > div.st-cmp-content")
        # Get the page content after any JavaScript has executed
        # page_content = await page.content()
        await page.waitForSelector('#vendor-settings > div:nth-child(2) > div > div:nth-child(2)') 
        text = await page.querySelector("#vendor-settings > div:nth-child(2) > div > div:nth-child(2)")
        await text.tap()
        await text.tap()
        
        # accept_button = await page.querySelector("#st-cmp-v2 > div > div.st-cmp-content > div > div.st-cmp-nav-buttons > div.st-cmp-permanent-footer-nav-buttons > div:nth-child(1)")
        reject_button = await page.querySelector("#st-cmp-v2 > div > div.st-cmp-content > div > div.st-cmp-nav-buttons > div.st-cmp-permanent-footer-nav-buttons > div:nth-child(2)")
        await reject_button.click()
        popup = await page.querySelector("#st-cmp-v2 > div > div.st-cmp-content")
        # print("popup", popup)
        if popup is not None and retries > 0:
            await self.clear_first_popup(page, retries - 1)
        
    async def __pass_vertical(self, page: Page, retries: int = 10):
        try:
            #TODO down section only for manga reading
            
            vertical = await page.querySelector("#first-read > div.read-tips > div > div.rtl-rows > a:nth-child(1)")
            # print("vertical", vertical)
            if vertical is not None and retries > 0:
                await vertical.click()
                await self.__pass_vertical(page, retries - 1)
        except:
            pass
                
    async def search_for_manga(self, page: Page, manga_name: str, max_results: int = 5):
        await page.goto(f"https://mangareader.to/search?keyword={manga_name}")
        
        await page.waitForSelector("#main-content > section > div.manga_list-sbs > div.mls-wrap")
        found_mangas = await page.querySelectorAll("div.mls-wrap > div.item > div.manga-detail > h3.manga-name > a")
        names: List[str] = []
        hrefs: List[str] = []
        for index, signle_manga in enumerate(found_mangas):
            name = await page.evaluate('(a) => a.textContent', signle_manga)
            href = await page.evaluate('(a) => a.href', signle_manga)
            names.append(name)
            hrefs.append(href)
            if index == (max_results - 1):
                break
        return names, hrefs

    async def get_chapters_or_volumes(self, page: Page, volume_mode: bool = False):
        selector_to_wait = "#en-chapters"
        href_selector = "#en-chapters > li:nth-child(1) > a"
        if volume_mode:
            selector_to_wait = "#en-volumes"
            href_selector = "#en-volumes > div:nth-child(1) > div.manga-poster > a"
            
        await page.waitForSelector(selector_to_wait)
        
        items_list = await page.querySelector(selector_to_wait)
    
        items_length = await page.evaluate('(item) => item.children.length', items_list)
        href = await page.querySelector(href_selector)
        href_example = await page.evaluate('(item) => item.href', href)
        return items_length, href_example
        
    
    async def download_content(self, page: Page, folder_to_save: str, on_start: FunctionType, on_progress: FunctionType, on_error: FunctionType):
        try:
            await self.__pass_vertical(page)
            
            await page.waitForSelector("#vertical-content", options={"timeout":3000})
            vertical_content = await page.evaluate("""document.querySelector("#vertical-content").children""")
            # print("vertical_content", len(vertical_content))
            if on_start is not None:
                on_start(len(vertical_content))
            
            format_width: int = len(str(len(vertical_content)))
            
            for index, item in enumerate(vertical_content):
                # print("index", index, "item", item)
                vertical_item = await page.evaluate(f"""document.querySelector("#vertical-content").children[{index}]""")
                # print("vertical_item", vertical_item == {})
                while vertical_item == {}:
                    vertical_item = await page.evaluate(f"""document.querySelector("#vertical-content").children[{index}]""")
                    await page.evaluate("""window.scrollBy(0, window.innerHeight)""")
                    await asyncio.sleep(0.2)
                
                await page.waitForSelector(f"#vertical-content > div:nth-child({index + 1}) > :nth-child(2)")
                item_to_download = await page.querySelector(f"#vertical-content > div:nth-child({index + 1}) > :nth-child(2)")
                tag_name = await page.evaluate('(element) => element.tagName', item_to_download)
                if tag_name.lower() == "canvas":
                    await self.__download_canvas(page, item_to_download, index, folder_to_save, format_width)
                elif tag_name.lower() == "img":
                    await self.__download_img(page, item_to_download, index, folder_to_save, format_width)
                else:
                    print(f"Unknown tag {tag_name}")
                
                if on_progress is not None:
                    on_progress(index)
        except Exception as e:
            await page.screenshot({"path":"download-fail.png"})
            print(e)
            if on_error is not None:
               on_error(f"{e}")
           
    async def __download_canvas(self, page: Page, canvas, index, folder_to_save, format_width: int):
        if canvas is None:
            print(f"canvas {index} is None!")
            return
        
        png_data = await page.evaluate('(canvas) => canvas.toDataURL("image/png")', canvas)

        # Decode the base64 data and save it as a PNG file
        png_data = png_data.split(',')[1]
        png_bytes = base64.b64decode(png_data)

        # Save the PNG image to a file
        formatted_index = "{:0{width}}".format(index, width=format_width)
        file_path = f'{folder_to_save}/{formatted_index}.png'
        with open(file_path, 'wb') as file:
            file.write(png_bytes)
        # print(f'Saved {file_path}')
        
    async def __download_img(self, page: Page, img, index, folder_to_save, format_width: int):
        image_url = await page.evaluate('(img) => img.src', img)
        response = requests.get(image_url)
        if response.status_code == 200:
            # Save the image content to the specified output file
            formatted_index = "{:0{width}}".format(index, width=format_width)
            file_path = f'{folder_to_save}/{formatted_index}.png'
            with open(file_path, 'wb') as file:
                file.write(response.content)
                
    async def get_item_url(self, page: Page, item_href_example: str, index: int, is_volume: bool = False):
        prefix = "Volume" if is_volume else "Chapter"
        return f"{get_href_no_last_part(item_href_example)}/{prefix.lower()}-{index}"