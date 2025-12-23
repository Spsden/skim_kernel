import xml.etree.ElementTree as et
from typing import List, Dict, Any, Optional

from rss_feeds.config.feed_urls import THE_HINDU_DEFAULT_HOME
from rss_feeds.core.base_parser import BaseNewsFeedParser


class TheHinduParser(BaseNewsFeedParser):
    def __init__(self):
        super().__init__(feed_url=THE_HINDU_DEFAULT_HOME, source_name="The Hindu")
        self.config["max_description_length"] = 800
        self.config["extract_images"] = True
        self.namespaces = {
            "atom": "http://www.w3.org/2005/Atom",
            "media": "http://search.yahoo.com/mrss/",
        }
        for prefix, uri in self.namespaces.items():
            et.register_namespace(prefix, uri)

    def _parse_specific_feed(self, root: et.Element) -> List[Dict[str, Any]]:
        articles = []
        channel = root.find("channel")

        feed_info = {
            "title": self._clean_html(channel.findtext("title")),
            "link": channel.findtext("link"),
            "description": self._clean_html(channel.findtext("description")),
            "language": channel.findtext("language"),
            "last_build_date": self._parse_datetime(channel.findtext("lastBuildDate")),
            "articles": [],
        }

        for item in channel.findall("item"):
            try:
                article = {
                    "source": "The Hindu",
                    "title": self._clean_html(item.findtext("title")),
                    "link": item.findtext("link"),
                    "description": self._clean_html(item.findtext("description")),
                    "pub_date": self._parse_datetime(item.findtext("pubDate")),
                    "image_url": (
                        self.extract_image_url(item)
                        if self.config["extract_images"]
                        else None
                    ),
                    "categories": self._extract_categories(item),
                    "article_id": self._extract_article_id(item),
                }

                if not self._validate_url(article["link"]):
                    self.logger.warning(f"Skipping invalid article: {article['title']}")
                    continue

                feed_info["articles"].append(article)
            except Exception as e:
                self.logger.error(f"Error parsing article: {e}")
                continue

        return feed_info["articles"]

    def _extract_categories(self, item: et.Element) -> List[str]:
        categories = []
        for category in item.findall("category"):
            cat_text = self._clean_html(category.text)
            if cat_text:
                categories.append(cat_text)
        return categories

    def _extract_article_id(self, item: et.Element) -> Optional[str]:
        guid = item.find("guid")
        if guid is not None:
            return guid.text.replace("article-", "")
        return None

    def extract_image_url(self, item: et.Element) -> Optional[str]:
        image_info = {
            "url": None,
            "type": None,
            "width": None,
            "height": None,
            "caption": None,
        }
        media_content = item.find("media:content", self.namespaces)
        if media_content is not None:
            image_info.update(
                {
                    "url": media_content.get("url"),
                    "type": media_content.get("type"),
                    "width": media_content.get("width"),
                    "height": media_content.get("height"),
                    "caption": self._clean_html(
                        media_content.findtext(
                            "media:description", namespaces=self.namespaces
                        )
                    ),
                }
            )
        return image_info["url"]

    def get_articles(self):
        parser = TheHinduParser()
        try:
            articles = parser.parse_feed()
            return articles
        except Exception as e:
            self.logger.error(f"Error at The Hindu feed: {e}")
            return []


def main():

    parser = TheHinduParser()

    try:
        articles = parser.parse_feed()

        print(f"Total articles parsed: {len(articles)}")
        for idx, article in enumerate(articles, 1):
            print(f"\nArticle {idx}:")
            print(f"Title: {article['title']}")
            print(f"Link: {article['link']}")
            print(f"Published: {article['pub_date']}")
            print(f"Image URL: {article.get('image_url', 'No image')}")
            print(f"Categories: {', '.join(article.get('categories', []))}")
            print(f"Article ID: {article.get('article_id', 'N/A')}")
            print(f"Description: {article['description'][:200]}...")

    except Exception as e:
        print(f"Error processing feed: {e}")


if __name__ == "__main__":
    main()
