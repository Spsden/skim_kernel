from database.connection import DBConnection
from dotenv import load_dotenv
from config.env import get_env
from temp import article
import logging
from msg_queue.queue_handler import QueueHandler
from scraper.pre_processing.toi.toi_pre_processing import TOIPreprocessing
import sys
import asyncio
from config.config import service_names
from database.connection import DBConnection
from llm_explorer.model_handler import ModelHandler
from config.config import queue_names
import json
import time
from database.repository.summarized_articles import PresummarizedArticleRepository


def main():
    """
    Accepts data from scraper_to_llm queue
    calls model to summarize body
    store summarized article body into database
    """

    service_name = service_names["summarization_service"]

    logger = logging.getLogger(f"LLM service: {service_name} ")

    try:

        # model instance
        model_handler = ModelHandler()

        # queue from scraping service
        channel_name = queue_names["scraping_to_summmarisation"]
        scraping_to_summ_queue = QueueHandler(channel_name)

        database_engine = DBConnection().get_engine()

        def handle_queue_body(body):
            """
            Gets queue and passes it to model for summarization
            """

            # parse string to json / dict
            unsummarized_artile_data = json.loads(body)

            if unsummarized_artile_data is None:
                return

            article_id = unsummarized_artile_data["id"]

            raw_article_id = unsummarized_artile_data["raw_article_id"]

            article_body = unsummarized_artile_data["body"]

            logger.info(f"Article {article_id} recieved")

            if article_body is None or article_id is None:
                logger.error(f"{channel_name} data is corrupted, missed some fields")
                return

            if raw_article_id is None:
                logger.warning(
                    f"{channel_name} raw_article_id is missing for {article_id}"
                )

            logger.info(f"Article {article_id} transfered to LLM for summarization")

            # to check how much time model takes to summarize 1 article
            summarization_start_time = time.perf_counter()

            summarized_article_body = model_handler.summarize_article(article_body)

            summarization_end_time = time.perf_counter()

            time_taken = summarization_end_time - summarization_start_time

            logger.info(
                f"Article: {article_id}\nTime taken to summarize: {time_taken:.4f}s"
            )

            if summarized_article_body is None:
                logger.warning(f"Summarization failed for ariticle: {article_id}")
                return

            # insert into database
            PresummarizedArticleRepository().update_body(
                id=article_id,
                engine=database_engine,
                article_body=summarized_article_body,
            )

            print("hello wlrd")

        scraping_to_summ_queue.consume(call_back=handle_queue_body)

        # model_handler.summarize_article()

    except Exception as e:
        logger.error(f"Main fun {str(e)}")
        raise e
