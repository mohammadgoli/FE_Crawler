import logging
import time
from utils import init_db, get_next_url_to_process, update_url_status
from freepikCrawler.src.scraper import FreepikScraper
from envatoCrawler.src.scraper import EnvatoScraper


def setup_logging(log_file):
    logging.basicConfig(filename=log_file, level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')


def get_crawler(url, config):
    if 'freepik.com' in url:
        return FreepikScraper(config)
    elif 'envato.com' in url:
        return EnvatoScraper(config)
    else:
        return None


if __name__ == "__main__":

    # Change this part for custom configurations:
    config = {
        'output_dir': "./output",
        'log_file': "./logs/scraper.log",
        'start_id': 1,
        'proxy': {
            # 'https': 'https://8.219.97.248:80',
        },
        'crawl_delay': 5  # Delay in seconds between each URL crawl
    }

    setup_logging(config['log_file'])
    init_db()

    start_time = time.time()

    while True:
        url = get_next_url_to_process()
        if not url:
            logging.info("No more URLs to process. Exiting.")
            break

        scraper = get_crawler(url, config)

        if scraper:
            print("scraping {}".format(url))
            scraper.run(url)
        else:
            logging.error(f"No suitable scraper found for URL: {url}")
            # Update status to -1 (No suitable scraper)
            update_url_status(url, -1)

        logging.info(f"Waiting for {config['crawl_delay']} seconds before crawling the next URL...")
        time.sleep(config['crawl_delay'])

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"Total time taken for all runs: {elapsed_time} seconds")
