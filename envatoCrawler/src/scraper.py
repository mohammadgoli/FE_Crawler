from utils import add_processed_url, save_parsed_data, update_url_status
import logging
import os
import json
from .downloader import HTMLDownloader
from .parser import EnvatoParser
from pathlib import Path
import sys

# Add the root directory to the sys.path
root_dir = Path(__file__).resolve().parents[2]
sys.path.append(str(root_dir))

# Now you can import from the root-level utils.py


class EnvatoScraper:
    def __init__(self, config):
        self.output_dir = config['output_dir']
        self.downloader = HTMLDownloader(self.output_dir)
        self.parser = EnvatoParser()

    def run(self, url):
        # Get the ID from the database
        page_id = add_processed_url(url)
        if not page_id:
            logging.error(f"Failed to add URL {url} to the database")
            return

        print(f"Downloading {url}")
        logging.info(f"Downloading page {page_id} from {url}")
        html_path = self.downloader.download_page(url, page_id)
        if html_path:
            print(f"Parsing {url}")
            logging.info(f"Parsing page {page_id}")
            data = self.parser.parse(html_path, url)
            if data:
                self.save_data(data, page_id)
                # Update URL status to parsed (status 2)
                update_url_status(url, 2)
            else:
                logging.error(f"Failed to parse data for page {page_id}")
                # Update URL status to error (status -1)
                update_url_status(url, 1)
        else:
            logging.error(f"Failed to download page {page_id}")
            # Update URL status to error (status -1)
            update_url_status(url, 0)

    def save_data(self, data, page_id):
        output_file = os.path.join(self.output_dir, 'data', 'envato', f"{page_id}.json")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=4)
        # Save parsed data to the database
        save_parsed_data(data, crawler_type='envato')
        logging.info(f"Data saved for page {page_id}")
