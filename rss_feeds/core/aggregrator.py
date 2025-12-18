from typing import List, Dict, Any
import logging
from webbrowser import get


from database.connection import DBConnection
from database.models.models import RawArticles
from database.repository.raw_articles import RawArticleRepository
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
            print("-" * 100)
            print(article)

    # def push_to_database(self, articles: List[Dict[str, Any]]):
    #     """
    #         To push fetched data to database
    #     """

    #     parsed_articles: List[RawArticles] = []

    #     # parsing data into accepatable list
    #     for article in articles:

                # parsed_article = RawArticles(
                #     title = article.get("title", "NA"),

                #     article_url = article.get("link", "NA"),

                #     source = article.get("source", "NA"),

                #     image_url = article.get("image_url", "NA"),

                #     published_date = article.get("pub_date", "NA"),
                # )

    #             parsed_articles.append(parsed_article)
            

        
    #     # inserting into database 
    #     try:
    #         database_engine = DBConnection.get_engine()

    #         RawArticleRepository.insert(database_engine, parsed_articles)

    #         self.logger.info("Articles sucessfully inserted into database")
                

    #     except Exception as e:
    #         self.logger.error(f"Database insertion failed: {str(e)}")


    # def get_articles(self, print_articles = False):
    #     logging.basicConfig(level=logging.INFO)

    #     parsers: List[BaseNewsFeedParser] = [
    #         # TheHinduParser(),
    #         TimesOfIndiaParser(),
    #         # IndiaTodayRSSParser(),
    #         # BBCParser(),
    #     ]


    #     aggregator = FeedAggregator(parsers)

    #     articles = aggregator.aggregate_feeds()

    #     if print_articles:
    #         aggregator.print_aggregated_articles(articles=articles)
            

    #     return articles






def get_articles_and_push_to_database():
    logging.basicConfig(level=logging.INFO)

    parsers: List[BaseNewsFeedParser] = [
        # TheHinduParser(),
        TimesOfIndiaParser(),
        # IndiaTodayRSSParser(),
        # BBCParser(),
    ]

    aggregator = FeedAggregator(parsers)

    aggregated_articles = aggregator.aggregate_feeds()

    # print(f"Number of articles fetched {len(aggregated_articles)}")
    # aggregator.print_aggregated_articles(aggregated_articles)

    return aggregated_articles
    # aggregator.push_to_database(aggregated_articles)


