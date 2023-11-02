from enum import Enum
import os
class Args:
    def __init__(self, runCommandName: str, type, help: str, required: bool = False, envName: str = None, default: str = None) -> None:
        self.runName = runCommandName
        self.type = type
        self.help = help
        self.required = required
        self.envName = envName
        self.default = default
    
    def get_default(self):
        if self.envName is not None:
            return os.environ.get(self.envName)
        return self.default
        
class ARGS_ENUM(Enum):
    SAVE_DIR = Args('--save_dir', str, 'The directory to save the manga. (REQUIRED)', True)
    MANGA_NAME = Args('--manga_name', str, "The name of the manga to download. (REQUIRED)", True, 'MANGA_NAME')
    MANGA_URL = Args('--manga_url', str, "The url of the manga to download.", False, 'MANGA_URL')
    DOWNLOAD_AMOUNT = Args('--download_amount', str, 'The amount of volumes/chaters that will be downloaded. (Example - All / 1 / 2-3 / 1,3-5,7-9)', False, 'DOWNLOAD_AMOUNT')
    
