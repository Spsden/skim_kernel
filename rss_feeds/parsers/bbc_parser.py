import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import xml.etree.ElementTree as et
import re
import html

from rss_feeds.config.feed_urls import BBC_HOME
from rss_feeds.core.base_parser import BaseNewsFeedParser


class BBCParser(BaseNewsFeedParser):
    def __init__(self):
        super().__init__(feed_url=BBC_HOME, source_name="BBC")
        self.config["max_description_length"] = 800  # Shorter descriptions
        self.config["extract_images"] = True

    def _parse_specific_feed(self, root: et.Element) -> List[Dict[str, Any]]:
        articles = []

        channel = root.find("channel")

        for item in channel.findall("item"):
            try:
                description = self._clean_html(item.findtext("description"))
                image_url = self.extract_image_url(item)
                description = self.clean_description(description)

                article = {
                    "source": "BBC",
                    "title": self._clean_html(item.findtext("title")),
                    "description": description,
                    "link": item.findtext("link"),
                    "guid": item.findtext("guid"),
                    "pub_date": self._parse_date(item.findtext("pubDate")),
                    "image_url": image_url,
                }

                if (
                    not article["title"]
                    or not article["link"]
                    or not self._validate_url(article["link"])
                ):
                    self.logger.warning(f"Skipping invalid article: {article['title']}")
                    continue

                articles.append(article)
            except Exception as e:
                self.logger.error(f"Error parsing article: {e}")
                continue

        return articles

    def get_articles(self):
        parser = BBCParser()
        try:
            articles = parser.parse_feed()
            return articles

        except Exception as e:
            self.logger.error(f"Error at BBC: {e}")
            print(f"from inda_today : {e}")

    def extract_image_url(self, item) -> Optional[str]:
        """Extract thumbnail image URL from the <media:thumbnail> tag"""
        thumbnail = item.find(
            "media:thumbnail", namespaces={"media": "http://search.yahoo.com/mrss/"}
        )
        if thumbnail is not None and "url" in thumbnail.attrib:
            return thumbnail.attrib["url"]
        return None

    def clean_description(self, text: Optional[str]):
        cleaned_text = re.sub(r"<a[^>]*>.*?</a>", "", text)
        cleaned_text = re.sub(r"<img[^>]*>", "", cleaned_text)
        cleaned_text = re.sub(r"<[^>]+>", "", cleaned_text)
        cleaned_text = html.unescape(cleaned_text)
        cleaned_text = " ".join(cleaned_text.split())
        return cleaned_text

    def _parse_date(self, date_str: str) -> str:
        try:
            dt = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S GMT")
            return dt.isoformat()
        except (ValueError, TypeError):
            self.logger.warning(f"Could not parse date: {date_str}")
            return None


#
# def main():
#     logging.basicConfig(
#         level=logging.INFO,
#         format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
#     )
#
#     parser = BBCParser()
#
#     try:
#         # Parse the feed
#         articles = parser.parse_feed()
#
#         # Print parsed articles
#         print(f"Total articles parsed: {len(articles)}")
#         for idx, article in enumerate(articles, 1):
#             print(f"\nArticle {idx}:")
#             print(f"Title: {article['title']}")
#             print(f"Link: {article['link']}")
#             print(f"Published: {article['pub_date']}")
#             print(f"Image URL: {article.get('image_url', 'No image')}")
#             print(f"Description: {article['description'][:200]}...")
#
#     except Exception as e:
#         print(f"Error processing feed: {e}")
#
#
# if __name__ == "__main__":
#     main()
