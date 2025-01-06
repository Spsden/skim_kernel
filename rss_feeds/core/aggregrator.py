from typing import List, Dict, Any
import logging

from rss_feeds.core.base_parser import BaseNewsFeedParser
from rss_feeds.parsers.bbc_parser import BBCParser
from rss_feeds.parsers.india_today_parser import IndiaTodayRSSParser
from rss_feeds.parsers.the_hindu_parser import TheHinduParser
from rss_feeds.parsers.toi_parser import TimesOfIndiaParser


class FeedAggregator:
    def __init__(self, parsers: List[BaseNewsFeedParser]):
        self.parsers = parsers
        self.logger = logging.getLogger("FeedAggregator")

    def aggregate_feeds(self) -> List[Dict[str, Any]]:
        aggregated_articles = []
        for parser in self.parsers:
            try:
                self.logger.info(f"Parsing feed from {parser.source_name}")
                articles = parser.get_articles()
                aggregated_articles.extend(articles)
                self.logger.info(f"Successfully parsed {len(articles)} articles from {parser.source_name}")
            except Exception as e:
                self.logger.error(f"Error parsing feed from {parser.source_name}: {e}")

        return aggregated_articles

    def print_aggregated_articles(self, articles: List[Dict[str, Any]]):
        for article in articles:
            print(article)



def main():
    logging.basicConfig(level=logging.INFO)

    parsers = [
        TheHinduParser(),
        TimesOfIndiaParser(),
        IndiaTodayRSSParser(),
        BBCParser(),
    ]

    aggregator = FeedAggregator(parsers)

    aggregated_articles = aggregator.aggregate_feeds()

    print(f"Number of articles fetched {len(aggregated_articles)}")
    aggregator.print_aggregated_articles(aggregated_articles)

if __name__ == "__main__":
    main()
