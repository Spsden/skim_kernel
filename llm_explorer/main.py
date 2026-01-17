import asyncio
import json
import logging
import threading
import time
from typing import Optional

from config.config import queue_names, service_names
from config.env import get_env
from database.connection import DBConnection
from database.repository.summarized_articles import PresummarizedArticleRepository
from dotenv import load_dotenv
from llm_explorer.summarizer_factory import create_summarizer
from msg_queue.queue_handler import QueueHandler


# Global event loop and thread for async operations
_event_loop: Optional[asyncio.AbstractEventLoop] = None
_loop_thread: Optional[threading.Thread] = None
_loop_lock = threading.Lock()
_loop_ready = threading.Event()


def _run_event_loop():
    """Run the event loop in a background thread."""
    global _event_loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    _event_loop = loop
    _loop_ready.set()  # Signal that the loop is ready
    loop.run_forever()


def get_event_loop() -> asyncio.AbstractEventLoop:
    """
    Get or create the persistent event loop for async operations.

    Starts a background thread with a long-running event loop on first call.
    Subsequent calls return the existing loop.

    Returns:
        The event loop running in the background thread.
    """
    global _loop_thread

    with _loop_lock:
        if _event_loop is None or _event_loop.is_closed():
            _loop_ready.clear()
            _loop_thread = threading.Thread(
                target=_run_event_loop, name="AsyncEventLoopThread", daemon=True
            )
            _loop_thread.start()
            # Wait for the loop to be ready
            _loop_ready.wait(timeout=5)

    return _event_loop


def stop_event_loop():
    """
    Stop the background event loop and cleanup resources.

    Call this before program exit to ensure clean shutdown.
    """
    global _event_loop, _loop_thread

    with _loop_lock:
        if _event_loop is not None and not _event_loop.is_closed():
            _event_loop.call_soon_threadsafe(_event_loop.stop)
            _event_loop.close()
            _event_loop = None

        if _loop_thread is not None and _loop_thread.is_alive():
            _loop_thread.join(timeout=2)
            _loop_thread = None


async def process_article(
    model_handler, article_body: str, article_id: str, logger: logging.Logger
) -> Optional[str]:
    """
    Process a single article asynchronously.

    Args:
        model_handler: The summarizer instance.
        article_body: The article text to summarize.
        article_id: The article identifier for logging.
        logger: Logger instance.

    Returns:
        The summarized article, or None if failed.
    """
    # to check how much time model takes to summarize 1 article
    summarization_start_time = time.perf_counter()

    summarized_article_body = await model_handler.summarize_article(article_body)

    summarization_end_time = time.perf_counter()

    time_taken = summarization_end_time - summarization_start_time

    logger.info(
        f"Article: {article_id}\nTime taken to summarize: {time_taken:.4f}s"
    )

    return summarized_article_body


def main():
    """
    Accepts data from scraper_to_llm queue
    calls model to summarize body
    store summarized article body into database
    """

    service_name = service_names["summarization_service"]

    logger = logging.getLogger(f"LLM service: {service_name} ")

    try:
        # model instance - uses factory to create appropriate summarizer
        # Uses SUMMARIZER_BACKEND env var or defaults to "openrouter"
        model_handler = create_summarizer()

        logger.info(
            f"Summarizer initialized: {model_handler.get_model_name()}"
        )

        # queue from scraping service
        channel_name = queue_names["scraping_to_summmarisation"]
        scraping_to_summ_queue = QueueHandler(channel_name)

        database_engine = DBConnection().get_engine()

        def handle_queue_body(body):
            """
            Gets queue and passes it to model for summarization.
            Bridges synchronous queue callback with async summarization.
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

            # Run async summarization in the persistent event loop
            loop = get_event_loop()
            future = asyncio.run_coroutine_threadsafe(
                process_article(model_handler, article_body, article_id, logger),
                loop,
            )

            # Block until the coroutine completes (with timeout)
            try:
                summarized_article_body = future.result(timeout=60)
            except asyncio.TimeoutError:
                logger.error(f"Summarization timeout for article: {article_id}")
                future.cancel()
                return
            except Exception as e:
                logger.error(
                    f"Summarization failed for article {article_id}: {str(e)}",
                    exc_info=True,
                )
                return

            if summarized_article_body is None:
                logger.warning(f"Summarization failed for ariticle: {article_id}")
                return

            # insert summary into database
            PresummarizedArticleRepository().update_summary(
                id=article_id,
                engine=database_engine,
                summary=summarized_article_body,
            )

        scraping_to_summ_queue.consume(call_back=handle_queue_body)

    except Exception as e:
        logger.error(f"Main function error: {str(e)}", exc_info=True)
        raise
    finally:
        # Clean up resources
        if "model_handler" in locals() and hasattr(model_handler, "close"):
            loop = get_event_loop()
            if loop and not loop.is_closed():
                future = asyncio.run_coroutine_threadsafe(
                    model_handler.close(), loop
                )
                try:
                    future.result(timeout=5)
                except Exception as e:
                    logger.warning(f"Error closing model_handler: {e}")

        # Stop the background event loop
        stop_event_loop()
        logger.info("Event loop stopped and resources cleaned up.")

