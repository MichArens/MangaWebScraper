from abc import ABC, abstractmethod
from types import FunctionType
from pyppeteer.page import Page

class BasePluginAgent(ABC):
    
    def __init__(self) -> None:
        self.home_url = None
    
    @abstractmethod
    async def clear_first_popup(self, page: Page, retries: int = 5):
        pass
    
    @abstractmethod            
    async def search_for_manga(self, page: Page, manga_name: str, max_results: int = 5):
        pass
    
    @abstractmethod            
    async def get_chapters_or_volumes(self, page: Page, volume_mode: bool = False):
        pass
     
    @abstractmethod           
    async def download_content(self, page: Page, folder_to_save: str, on_start: FunctionType, on_progress: FunctionType, on_error: FunctionType):
        pass