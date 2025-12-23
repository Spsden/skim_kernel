import logging
from config.config import queue_names
from msg_queue.queue_handler import QueueHandler
from scraper.pre_processing.toi.toi_pre_processing import TOIPreprocessing
from config.env import get_env
import json
from typing import List
from database.models.models import SummarizedArticles


def main():

    from config.config import service_names

    service_name = service_names["scraping_service"]

    logger = logging.getLogger(f"Scraping Service: {service_name}")

    try:
        # get data from rss queue
        queue_name_with_incomming_data = queue_names["rss_to_scraping"]
        incomming_queue = QueueHandler(queue_name_with_incomming_data)

        # queue for summmarization service
        queue_name_summarization_service = queue_names["scraping_to_summmarisation"]
        queue_to_summarization = QueueHandler(queue_name_summarization_service)

        from database.connection import DBConnection

        engine = DBConnection().get_engine()

        def data_reciever(body):
            """
            Function to handle recieved data from rss service and
            get body and other meta data and insert data and send
            to summarization service.
            """
            article_in_json_format = json.loads(body)

            # if recieved article is valid json and has article link
            if article_in_json_format and article_in_json_format["link"]:

                article_url = article_in_json_format["link"]

                scraping_handler = TOIPreprocessing(article_url)

                # to get all data primrly body
                scraped_article_with_body = scraping_handler.get_article_data()

                if scraped_article_with_body is None:
                    logger.warning(f"Article scraping failed")
                    return

                # TODO: in later releases upload non-summarized body onto aws string in file
                parsed_article = SummarizedArticles(
                    title=scraped_article_with_body.get("title")
                    or article_in_json_format["title"]
                    or "",
                    article_url=article_in_json_format["link"] or None,
                    source=article_in_json_format["source"] or "Bhanu",
                    img_src=article_in_json_format["image_url"] or None,
                    published_date=article_in_json_format["pub_date"]
                    or scraped_article_with_body.get("published_date", None),
                    raw_article_id=article_in_json_format["raw_article_id"] or None,
                    # TODO: call llm or check for category
                )

                # push articles meta data to database
                from database.repository.summarized_articles import (
                    PresummarizedArticleRepository,
                )

                article_id = PresummarizedArticleRepository.insert(
                    engine=engine, data=parsed_article
                )

                if article_id is None:
                    logger.warn("Data insertion failed.")
                    return

                # send id with body to summarization service
                queue_to_summarization.publisher(
                    {
                        "id": article_id,
                        "body": scraped_article_with_body.get("body"),
                        "raw_article_id": article_in_json_format["raw_article_id"],
                    }
                )

        incomming_queue.consume(call_back=data_reciever)

        logger.info("Data extraction completed")

    except Exception as e:
        logger.error(f"Error in {service_name}")
        raise e
