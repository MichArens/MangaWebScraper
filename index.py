import asyncio
import os
from services.volume_download_service import VolumeDownloadService
    
if __name__ == '__main__':
    url = 'https://mangareader.to/read/ge-good-ending-1056/en/volume-1'  # Replace with the URL of the website
    save_dir = "downloaded_images"
    os.makedirs(save_dir, exist_ok=True)
    vds = VolumeDownloadService()
    asyncio.get_event_loop().run_until_complete(vds.run(url, save_dir))