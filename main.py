

from database.connection import DBConnection
from rss_feeds.core.aggregrator import get_articles_and_push_to_database
from dotenv import load_dotenv
from config.env import get_env
from llm_explorer.model_handler import ModelHandler
from temp import article
import logging
from msg_queue.queue_handler import QueueHandler
from scraper.pre_processing.toi.toi_pre_processing import TOIPreprocessing 
import sys
import asyncio
from config.config import service_names
from database.connection import DBConnection


load_dotenv()

async def main(service: str):
# Main function to run service which is selected or run all

  logger = logging.getLogger(f"Service: {service}")
  try:

    # db init
    database_url = get_env("DATABASE_URL")

    database_instance = DBConnection()
    database_instance.init(database_url)

    service = service.lower()

    # rss service exec
    if service == service_names["rss_service"]:
      # logic to run rss_service
      logger.info(f"Service {service} started")
      from rss_feeds.main import main
      main()
    #   asyncio.run(main())
    
    
    # scraping service exec
    elif service == service_names["scraping_service"]:
      # logic to run scraping service
      logger.info(f"Service {service} started")
      from scraper.main import main
      main()

    # summarization service exec
    elif service == service_names["summarization_service"]:
      # logic to run summarization_service
      logger.info(f"Service {service} started")
      from llm_explorer.main import main
      main()

    elif service == service_names["all_service"]:
      logger.info("All services is to be started")
      # try to multi thread

    else:
      logger.warn(f"{service} is not a valid service name, exiting handler")
      raise Exception(f"{service} is not a valid service name, exiting handler")
      


  except Exception as e:
    logger.error(f"{service} main fun error: {str(e)}")
    exit(1)



  

if __name__ == '__main__':
  logging.basicConfig(level=logging.INFO)

  args = sys.argv[1]
  print(f"Provided args {args}")
  
  if args is None:
    print("No sevice name were passed, defaulting to running all services")
    asyncio.run(main(service_names["all_service"]))

  asyncio.run(main(args))


