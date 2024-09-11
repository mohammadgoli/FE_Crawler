import os
from playwright.sync_api import sync_playwright


class HTMLDownloader:
    def __init__(self, output_dir):
        self.output_dir = os.path.join(output_dir, 'html')

    def download_page(self, url, page_id):
        file_path = os.path.join(self.output_dir, f"freepik/{page_id}.html")

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.110 Safari/537.36',
                    'Referer': 'https://www.google.com/',
                    'Accept-Language': 'en-US,en;q=0.9',
                })

                page.set_viewport_size({"width": 1920, "height": 1080})

                # Navigate with increased timeout and domcontentloaded wait state
                page.goto(url, timeout=60000, wait_until="domcontentloaded")

                # Wait for a specific element to ensure the page is loaded
                page.wait_for_selector("body", timeout=60000)

                html_content = page.content()

                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(html_content)

                print(f"Page downloaded: {file_path}")
                browser.close()
                return file_path

        except Exception as e:
            print(f"Exception occurred while downloading {url}: {e}")
            return None
