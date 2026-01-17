"""
Test producer for the summarization queue.
Pushes test articles to the RabbitMQ queue for processing.
"""

import json
import logging

from config.env import get_env
from msg_queue.queue_handler import QueueHandler
from config.config import queue_names

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("TestProducer")


# Test article
TEST_ARTICLE = """
SpaceX successfully launched its Starship rocket for the first time today,
marking a significant milestone in space exploration. The massive rocket,
designed to carry humans to Mars, lifted off from Texas at 8:00 AM CT.
The flight achieved several key objectives including stage separation and
reaching orbit. CEO Elon Musk called it a "historic day" for humanity.
NASA administrator Bill Nelson congratulated the team, noting the importance
of the achievement for future space missions. The Starship program has seen
multiple delays and setbacks over the past three years. Today's success
represents a major step forward for the commercial space industry.
"""


def push_test_article(article_id: int = 1, raw_article_id: int = 101):
    """Push a test article to the scraping -> summarization queue."""

    # Create message payload
    message = {
        "id": article_id,
        "raw_article_id": raw_article_id,
        "body": TEST_ARTICLE,
        "url": f"https://example.com/article/{article_id}",
        "title": f"Test Article {article_id}"
    }

    # Get queue name
    channel_name = queue_names["scraping_to_summmarisation"]

    # Initialize queue handler
    queue = QueueHandler(channel_name)

    # Encode and publish
    queue.publisher(message)

    logger.info(f"Published article {article_id} to queue '{channel_name}'")
    logger.info(f"Message: {json.dumps(message, indent=2)}")


if __name__ == "__main__":
    print("=" * 60)
    print("Queue Test Producer")
    print("=" * 60)
    print("\nMake sure the summarization service is running:")
    print("  make run-summ")
    print("  or: uv run python llm_explorer/main.py")
    print()

    try:
        # Push a test article
        push_test_article(article_id=999, raw_article_id=1001)
        print("\nTest article pushed to queue!")
        print("Check the summarization service logs for processing.")

    except Exception as e:
        logger.error(f"Failed to push to queue: {e}")
        import traceback
        traceback.print_exc()
