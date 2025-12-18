
import logging
from config.config import queue_names
from msg_queue.queue_handler import QueueHandler
from scraper.pre_processing.toi.toi_pre_processing import TOIPreprocessing
import json



def main():

  from config.config import service_names
  service_name = service_names["scraping_service"]

  logger = logging.getLogger(f"Scraping Service: {service_name}")

  try:
    # get data from rss queue
    queue_name_with_incomming_data = queue_names["rss_to_scraping"]

    incomming_queue = QueueHandler(queue_name_with_incomming_data)

    def data_reciever(body):
      
      print(f"body is {body}")
      print("*" * 100)

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
        
        # combining data recieved from rss and
        # details recived from scraping to send for summarization
        





        


        




        

      


      

      link = data_in_json["link"]

      print(f"link is {link}")
      

    incomming_queue.consume(call_back=data_reciever)

    logger.info("Data extraction completed")



    # get url for every article recieved

    # scrap data for body and other details

  except Exception as e:
    logger.error(f"Error in {service_name}")
    raise e


