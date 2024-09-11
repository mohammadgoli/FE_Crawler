import json
from bs4 import BeautifulSoup
import logging
import re


class FreepikParser:
    def parse(self, html_path, url):
        try:
            with open(html_path, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')

            # 1. Meta Title
            meta_title = soup.find('title').get_text(
            ) if soup.find('title') else None

            # 2. Meta Description
            meta_description_tag = soup.find(
                'meta', attrs={"name": "description"})
            meta_description = meta_description_tag['content'] if meta_description_tag else None

            # 3. Name of File (H1 tag content)
            name_of_file = soup.find('h1').get_text(
                strip=True) if soup.find('h1') else None

            # 4. Creator Info (author's name and link)
            creator_info_tag = soup.find(
                'a', attrs={"aria-label": "Link to the author's page"})
            creator_link = creator_info_tag['href'] if creator_info_tag else None

            if creator_link:
                # Extract the part of the URL after '/author/'
                match = re.search(r'/author/([^/]+)', creator_link)
                name_of_creator = match.group(1) if match else None
            else:
                name_of_creator = None

            # 5. Tags (Related tags)
            tags = {}
            related_tags_section = None
            related_tags_pattern = re.compile(r'Related\s*tags', re.IGNORECASE)

            for p_tag in soup.find_all('p'):
                if related_tags_pattern.search(p_tag.get_text()):
                    related_tags_section = p_tag
                    break

            if related_tags_section:
                ul_tag = related_tags_section.find_next('ul')
                if ul_tag:
                    for li in ul_tag.find_all('li'):
                        a_tag = li.find('a')
                        if a_tag:
                            tag_name = a_tag.get_text(strip=True)
                            tag_link = a_tag['href']
                            tags[tag_name] = tag_link
            else:
                logging.warning(f"Related tags section not found in: {html_path}")

            # 6. Attributes (File Types and Quality)
            attributes = {
                "file_types": [],
                "quality": None,
            }

            # Iterate through all span tags to find the file type and quality information
            for span in soup.find_all('span'):
                span_text = span.get_text(strip=True)

                # Handle "File" and "File type"
                if re.match(r'^File\s*type|^File\s*', span_text, re.IGNORECASE):
                    nested_span = span.find_next('span')
                    if nested_span:
                        nested_text = nested_span.get_text(strip=True)
                        self._extract_file_info(nested_text, attributes)
                elif re.match(r'^\s*File\s*$', span_text, re.IGNORECASE):
                    # The case where "File" is followed by another span with details
                    nested_span = span.find_next('span')
                    if nested_span:
                        nested_text = nested_span.get_text(strip=True)
                        self._extract_file_info(nested_text, attributes)

            # 7. Preview Link (based on og:image)
            preview_link = None
            og_image_tag = soup.find('meta', property="og:image")
            if og_image_tag and 'content' in og_image_tag.attrs:
                og_image_url = og_image_tag['content']
                if og_image_url.startswith('https://img'):
                    # Case 1: Image
                    preview_link = [og_image_url]
                elif og_image_url.startswith('https://cdn-icons-png'):
                    # Case 2: Icon
                    preview_link = [og_image_url]
                elif og_image_url.startswith('https://videocdn'):
                    # Case 3: Video, extract video source links
                    video_source_links = []
                    video_tags = soup.find_all(
                        'video', attrs={"controlslist": "nodownload"})
                    if video_tags:
                        for video_tag in video_tags:
                            source_tag = video_tag.find('source')
                            if source_tag and 'src' in source_tag.attrs:
                                video_source_links.append(source_tag['src'])
                    preview_link = video_source_links if video_source_links else None

            # 8. Video Details (Aspect Ratio, Frame Rate, Duration)
            for div in soup.find_all('div'):
                div_text = div.get_text(strip=True)
                if "Aspect ratio" in div_text:
                    attributes["aspect_ratio"] = self._extract_detail(
                        div_text, "Aspect ratio")
                if "Frame rate" in div_text:
                    attributes["frame_rate"] = self._extract_detail(
                        div_text, "Frame rate")
                if "Duration" in div_text:
                    attributes["duration"] = self._extract_detail(
                        div_text, "Duration")

            # Combine all extracted data into a dictionary
            data = {
                "url": url,
                "meta_title": meta_title,
                "meta_description": meta_description,
                "name_of_file": name_of_file,
                "name_of_creator": name_of_creator,
                "creator_link": creator_link,
                "tags": tags,
                "attributes": attributes,
                "preview_link": json.dumps(preview_link),
            }

            return data

        except Exception as e:
            logging.error(f"Error parsing HTML file {html_path}: {e}")
            return None

    def _extract_file_info(self, text, attributes):
        """Helper function to extract file types and quality from text."""
        # Split the text on '/'
        parts = [part.strip() for part in text.split('/')]

        def is_quality_or_file_type(part):
            letters = sum(c.isalpha() for c in part)
            digits = sum(c.isdigit() for c in part)
            # If number of digits > letters, it's a quality. Otherwise, it's a file type
            return "quality" if digits > letters else "file_type"

        if len(parts) == 2:  # This likely contains both quality and file types
            if is_quality_or_file_type(parts[0]) == "quality":
                attributes["quality"] = parts[0]
                attributes["file_types"].extend(
                    [ft.strip() for ft in parts[1].split(',')])
            else:  # In case the order is reversed or there’s a missing resolution
                attributes["file_types"].extend(
                    [ft.strip() for ft in parts[0].split(',')])
                attributes["file_types"].extend(
                    [ft.strip() for ft in parts[1].split(',')])

        elif len(parts) == 1:  # This is either just the quality or file types
            # Likely resolution
            if is_quality_or_file_type(parts[0]) == "quality":
                attributes["quality"] = parts[0]
            else:  # Just file types
                attributes["file_types"].extend(
                    [ft.strip() for ft in parts[0].split(',')])

    def _extract_detail(self, text, detail_type):
        """Extracts the specific detail (e.g., Aspect ratio) from the div text."""
        match = re.search(f'{detail_type}\s*(\d+:\d+|\d+\s*fps|\d{2}:\d{2})', text)
        return match.group(1) if match else None
