from typing import List, Dict, Any
import logging

from rss_feeds.core.base_parser import BaseNewsFeedParser


class FeedAggregator:
    def __init__(self, parsers: List[BaseNewsFeedParser]):
        self.parsers = parsers
        self.logger = logging.getLogger("FeedAggregator")

    def aggregate_feeds(self) -> List[Dict[str, Any]]:
        aggregated_articles = []
        for parser in self.parsers:
            try:
                self.logger.info(f"Parsing feed from {parser.source_name}")
                articles = parser.parse_feed()
                aggregated_articles.extend(articles)
                self.logger.info(f"Successfully parsed {len(articles)} articles from {parser.source_name}")
            except Exception as e:
                self.logger.error(f"Error parsing feed from {parser.source_name}: {e}")

        return aggregated_articles

    def print_aggregated_articles(self, articles: List[Dict[str, Any]]):
        for article in articles:
            print(f"{article['title']} - {article['source']} - {article['pub_date']}")
