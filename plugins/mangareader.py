import asyncio
import base64
from types import FunctionType
from pyppeteer.page import Page

class MangaReader:
    
    def __init__(self):
        pass
    
    async def pass_first(self, page: Page, retries: int = 5):
        await page.waitForSelector('#st-cmp-v2 .st-cmp-content .st-button .st-text')

        # Get the page content after any JavaScript has executed
        # page_content = await page.content()
        await page.waitForSelector('#vendor-settings > div:nth-child(2) > div > div:nth-child(2)') 
        text = await page.querySelector("#vendor-settings > div:nth-child(2) > div > div:nth-child(2)")
        await text.tap()
        await text.tap()
        
        # accept_button = await page.querySelector("#st-cmp-v2 > div > div.st-cmp-content > div > div.st-cmp-nav-buttons > div.st-cmp-permanent-footer-nav-buttons > div:nth-child(1)")
        reject_button = await page.querySelector("#st-cmp-v2 > div > div.st-cmp-content > div > div.st-cmp-nav-buttons > div.st-cmp-permanent-footer-nav-buttons > div:nth-child(2)")
        await reject_button.click()
        
        await page.waitForSelector("#first-read > div.read-tips > div > div.rtl-rows > a:nth-child(1)")
        
        vertical = await page.querySelector("#first-read > div.read-tips > div > div.rtl-rows > a:nth-child(1)")
        await vertical.click()
        #TODO fix sometimes doesn't work
        try:
            await page.waitForSelector("#vertical-content", options={"timeout": 3000})
        except Exception as e:
            if (retries == 0):
                raise e
            else:
                await page.screenshot({"path":f"pass_first_fail{retries}.png"})
                await self.pass_first(page, retries - 1)
                
    async def download_content(self, page: Page, folder_to_save: str, on_start: FunctionType, on_progress: FunctionType, on_error: FunctionType):
        try:
            await page.waitForSelector("#vertical-content")
            vertical_content = await page.evaluate("""document.querySelector("#vertical-content").children""")
            # print("vertical_content", len(vertical_content))
            if on_start is not None:
                on_start(len(vertical_content))
                
            for index, item in enumerate(vertical_content):
                # print("index", index, "item", item)
                vertical_item = await page.evaluate(f"""document.querySelector("#vertical-content").children[{index}]""")
                # print("vertical_item", vertical_item == {})
                while vertical_item == {}:
                    vertical_item = await page.evaluate(f"""document.querySelector("#vertical-content").children[{index}]""")
                    await page.evaluate("""window.scrollBy(0, window.innerHeight)""")
                    await asyncio.sleep(0.2)
                    
                await page.waitForSelector(f"#vertical-content > div:nth-child({index + 1}) > canvas")
                canvas_to_download = await page.querySelector(f"#vertical-content > div:nth-child({index + 1}) > canvas")
                await self.__download_canvas(page, canvas_to_download, index, folder_to_save)
                if on_progress is not None:
                    on_progress(index)
        except Exception as e:
           if on_error is not None:
               on_error(e)
           
    async def __download_canvas(self, page: Page, canvas, index, folder_to_save):
        if canvas is None:
            print(f"canvas {index} is None!")
            return
        
        png_data = await page.evaluate('(canvas) => canvas.toDataURL("image/png")', canvas)

        # Decode the base64 data and save it as a PNG file
        png_data = png_data.split(',')[1]
        png_bytes = base64.b64decode(png_data)

        # Save the PNG image to a file
        file_path = f'{folder_to_save}/canvas_{index + 1}.png'
        with open(file_path, 'wb') as file:
            file.write(png_bytes)
        # print(f'Saved {file_path}')