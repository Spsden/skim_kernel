import logging
from typing import List, Dict, Any, Optional
import xml.etree.ElementTree as et

from rss_feeds.config.feed_urls import INDIA_TODAY_HOME
from rss_feeds.core.base_parser import BaseNewsFeedParser
import re


class IndiaTodayRSSParser(BaseNewsFeedParser):
    def __init__(self):
        super().__init__(feed_url=INDIA_TODAY_HOME, source_name="India Today")
        self.config["max_description_length"] = 800  # Shorter descriptions
        self.config["extract_images"] = True

    def _parse_specific_feed(self, root: et.Element) -> List[Dict[str, Any]]:
        articles = []

        for item in root.findall(".//item"):
            try:
                article = {
                    "source": "India Today",
                    "title": self._clean_html(item.findtext("title")),
                    "link": item.findtext("link"),
                    "description": self._clean_html(item.findtext("description")),
                    "pub_date": self._parse_datetime(item.findtext("pubDate")),
                    "image_url": (
                        self.extract_image_url(
                            item.findtext("description"), INDIA_TODAY_HOME
                        )
                        if self.config["extract_images"]
                        else None
                    ),
                }

                articles.append(article)
            except Exception as e:
                self.logger.error(f"Error parsing article: {e}")
                continue

        return articles

    def get_articles(self):
        parser = IndiaTodayRSSParser()
        try:
            articles = parser.parse_feed()
            return articles

        except Exception as e:
            self.logger.error(f"Error at India today: {e}")

    def extract_image_url(self, item, source: Optional[str]) -> Optional[str]:
        clean_desc = re.search(r'<img[^>]+src="([^"]+)"', item)
        if clean_desc:
            return clean_desc.group(1)
        else:
            var = None


# def main():
#     logging.basicConfig(
#         level=logging.INFO,
#         format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
#     )
#
#     parser = IndiaTodayRSSParser()
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


# if __name__ == "__main__":
#     main()
