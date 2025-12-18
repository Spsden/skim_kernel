

from rss_feeds.core.base_parser import BaseNewsFeedParser
from rss_feeds.core.aggregrator import FeedAggregator
import logging
from typing import List
from config.config import queue_names
from rss_feeds.parsers.toi_parser import TimesOfIndiaParser
from msg_queue.queue_handler import QueueHandler

def main():
  from config.config import service_names

  service = service_names['rss_service']

  logger = logging.getLogger(f"RSS service: {service}")

  parsers: List[BaseNewsFeedParser] = [
        # TheHinduParser(),
        TimesOfIndiaParser(),
        # IndiaTodayRSSParser(),
        # BBCParser(),
  ]

  try:
    aggregator = FeedAggregator(parsers) 

    articles = aggregator.aggregate_feeds()
    
    # sending articles to scraper queue
    channel_name = queue_names["rss_to_scraping"]

    queue_handler = QueueHandler(channel_name=channel_name)

    logger.info(f"Articles count: {len(articles)}")

    for article in articles:
      queue_handler.publisher(article)

    logger.info(f"Articles are send to queue: {channel_name}")

  except Exception as e:
    logger.error(f"Error in {service}")
    raise e
