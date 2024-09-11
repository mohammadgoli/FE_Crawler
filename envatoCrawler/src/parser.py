import json
from bs4 import BeautifulSoup
import logging


class EnvatoParser:
    def parse(self, html_path, url):
        try:
            with open(html_path, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')

            # 1. Meta Title
            meta_title_tag = soup.find(
                'title', attrs={"data-elements-meta": "true"})
            meta_title = meta_title_tag.get_text() if meta_title_tag else None

            # 2. Meta Description
            meta_description_tag = soup.find(
                'meta', attrs={"data-elements-meta": "true", "name": "description"})
            meta_description = meta_description_tag['content'] if meta_description_tag else None

            # 3. File Name (H1 tag content)
            name_of_file = soup.find('h1').get_text(
            ).strip() if soup.find('h1') else None

            # 4. Creator Name and Link
            creator_info = soup.find('h1').find_next('span')
            if creator_info:
                name_of_creator = creator_info.get_text(
                    strip=True).replace('By', '').strip()
                creator_link = creator_info.find(
                    'a')['href'] if creator_info.find('a') else None
                creator_link = "https://envato.com" + str(creator_link)
            else:
                name_of_creator = None
                creator_link = None

            # 5. Breadcrumb
            breadcrumb = soup.find('div', attrs={"data-testid": "breadcrumbs"})
            breadcrumb_text = None
            breadcrumb_items = None
            second_phrase = None
            if breadcrumb:
                breadcrumb_items = [a.get_text(strip=True)
                                    for a in breadcrumb.find_all('a')]
                breadcrumb_text = ' / '.join(breadcrumb_items)
                second_phrase = breadcrumb_items[1] if len(
                    breadcrumb_items) > 1 else None

            # 6. Preview Link (Video, Music, or Image)
            preview_link = []

            # First, handle video or music preview link
            download_button_preview_link = soup.find(
                'a', attrs={"data-testid": "button-download-preview"}
            )
            if download_button_preview_link:
                preview_url = download_button_preview_link['href']
                preview_link.append(preview_url)

                # Check if the preview URL starts with 'video-previews'
                if preview_url.startswith('https://video-previews'):
                    # Find the video tag with a matching src
                    video_tag = soup.find('video', src=preview_url)
                    if video_tag and video_tag.has_attr('poster'):
                        # Add the poster link to the preview_link list
                        poster_link = video_tag['poster']
                        preview_link.append(poster_link)

            # Find all divs matching either of the two conditions for images/graphics
            target_divs = soup.find_all(lambda tag: (
                tag.name == 'div' and (
                    tag.get('data-testid') == 'default-image-preview-container' or
                    tag.has_attr('data-item-index')
                )
            ))

            # Loop through all target divs to find img tags
            for div in target_divs:
                img_tags = div.find_all(
                    'img', src=lambda x: x and 'envatousercontent.com' in x)
                preview_link.extend([img['src']
                                     for img in img_tags if 'src' in img.attrs])

            # 7. Tags with Links (based on second phrase of breadcrumb)
            tags = {}
            tag_search_term = f"{second_phrase}" if second_phrase != None else "*"
            for a_tag in soup.find_all('a', title=lambda t: t and t.endswith(tag_search_term)):
                tag_name = a_tag.get_text(strip=True)
                tag_link = a_tag['href']
                tags[tag_name] = tag_link

            # 8. Attributes
            attributes = {}
            # Locate the span containing "Attributes"
            attributes_span = soup.find('span', string="Attributes")
            if attributes_span:
                # Find the next div following the span
                attributes_div = attributes_span.find_next('div')
                if attributes_div:
                    # Extract dt (keys) and dd (values) from dl
                    for dl in attributes_div.find_all('dl'):
                        dt_tags = dl.find_all('dt')
                        dd_tags = dl.find_all('dd')
                        for dt, dd in zip(dt_tags, dd_tags):
                            key = dt.get_text(strip=True)
                            value = dd.get_text(strip=True)
                            attributes[key] = value

            # 9. Description (from nested divs)
            description = None
            description_tag = soup.find('p', string="Description")
            if description_tag:
                description_div = description_tag.find_next('div')
                if description_div:
                    description_text = description_div.get_text(strip=True)
                    description = description_text

            # Combine all extracted data
            data = {
                "url": url,
                "meta_title": meta_title,
                "meta_description": meta_description,
                "description": description,
                "name_of_file": name_of_file,
                "name_of_creator": name_of_creator,
                "creator_link": creator_link,
                "breadcrumb": json.dumps(breadcrumb_items),
                "preview_link": json.dumps(preview_link),
                "tags": tags,
                "attributes": attributes
            }

            return data

        except Exception as e:
            logging.error(f"Error parsing HTML file {html_path}: {e}")
            return None
