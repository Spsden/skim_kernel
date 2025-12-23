import logging
from typing import List, Dict, Any, Optional
import xml.etree.ElementTree as et

from rss_feeds.config.feed_urls import TIMES_OF_INDIA_HOME, TOI_TOP_STORIES
from rss_feeds.core.base_parser import BaseNewsFeedParser


class TimesOfIndiaParser(BaseNewsFeedParser):
    def __init__(self):
        super().__init__(
            feed_url=TIMES_OF_INDIA_HOME + TOI_TOP_STORIES, source_name="Times of India"
        )
        self.config["max_description_length"] = 800
        self.config["extract_images"] = True

    def _parse_specific_feed(self, root: et.Element) -> List[Dict[str, Any]]:
        articles = []

        for item in root.findall(".//item"):
            try:
                article = {
                    "source": "Times of India",
                    "title": self._clean_html(item.findtext("title")),
                    "link": item.findtext("link"),
                    "description": self._clean_html(item.findtext("description")),
                    "pub_date": self._parse_datetime(item.findtext("pubDate")),
                    "image_url": (
                        self.extract_image_url(item)
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
        parser = TimesOfIndiaParser()
        try:
            articles = parser.parse_feed()
            return articles

        except Exception as e:
            self.logger.error(f"Error at India today: {e}")
            print(f"from inda_today : {e}")

    def extract_image_url(self, item) -> Optional[str]:
        enclosure = item.find("enclosure")
        if enclosure is not None and "url" in enclosure.attrib:
            return enclosure.attrib["url"]
        return None


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    parser = TimesOfIndiaParser()

    try:
        articles = parser.parse_feed()

        print(f"Total articles parsed: {len(articles)}")
        for idx, article in enumerate(articles, 1):
            print(f"\nArticle {idx}:")
            print(f"Title: {article['title']}")
            print(f"Link: {article['link']}")
            print(f"Published: {article['pub_date']}")
            print(f"Image URL: {article.get('image_url', 'No image')}")
            print(f"Description: {article['description'][:200]}...")

    except Exception as e:
        print(f"Error processing feed: {e}")


if __name__ == "__main__":
    main()
