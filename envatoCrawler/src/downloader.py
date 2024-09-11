import os
import requests
import logging


class HTMLDownloader:
    def __init__(self, output_dir):
        self.output_dir = os.path.join(output_dir, 'html')
        os.makedirs(self.output_dir, exist_ok=True)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        }

    def download_page(self, url, page_id):
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            file_path = os.path.join(self.output_dir, f"envato/{page_id}.html")
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(response.text)
            logging.info(f"Downloaded page {page_id}")
            return file_path
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to download {url}: {e}")
            return None
