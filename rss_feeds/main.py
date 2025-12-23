from rss_feeds.core.base_parser import BaseNewsFeedParser
from rss_feeds.core.aggregrator import FeedAggregator
import logging
from typing import List
from config.config import queue_names
from rss_feeds.parsers.toi_parser import TimesOfIndiaParser
from msg_queue.queue_handler import QueueHandler
from config.env import get_env
from database.connection import DBConnection
from database.repository.raw_articles import RawArticleRepository
from database.models.models import RawArticles


def main():
    from config.config import service_names

    service_name = service_names["rss_service"]

    logger = logging.getLogger(f"RSS service: {service_name} ")

    parsers: List[BaseNewsFeedParser] = [
        # TheHinduParser(),
        TimesOfIndiaParser(),
        # IndiaTodayRSSParser(),
        # BBCParser(),
    ]

    try:
        aggregator = FeedAggregator(parsers)
        articles = aggregator.aggregate_feeds()

        # database
        database_engine = DBConnection().get_engine()

        # sending articles to scraper queue
        channel_name = queue_names["rss_to_scraping"]
        rss_to_scraping_queue = QueueHandler(channel_name=channel_name)

        logger.info(f"Articles count: {len(articles)}")

        for article in articles:
            # add to database
            raw_article = RawArticles(
                title=article.get("title", "NA"),
                article_url=article.get("link", "NA"),
                source=article.get("source", "NA"),
                image_url=article.get("image_url", "NA"),
                published_date=article.get("pub_date", "NA"),
            )

            raw_article_id = RawArticleRepository.insert(
                engine=database_engine, data=raw_article
            )

            if raw_article_id is None:
                continue

            # add raw article id to dict
            article["raw_article_id"] = raw_article_id

            # push to queue
            rss_to_scraping_queue.publisher(article)

        logger.info(f"Articles are send to queue: {channel_name}")

    except Exception as e:
        logger.error(f"Main fun {str(e)}")
        raise e
