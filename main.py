 # This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from database.connection import DBConnection
from rss_feeds.core.aggregrator import get_articles_and_push_to_database
from dotenv import load_dotenv
from config.env import get_env
from llm_handler.model_handler import ModelHandler
from temp import article
from msg_queue.handler import QueueHandler
from scraper.pre_processing.toi_pre_processing import TOIPreprocessing 
load_dotenv()


if __name__ == '__main__':


    try:
        # database_url: str = get_env("DATABASE_URL")

        # db_engine = DBConnection.init(database_url=database_url)

        # # get_articles_and_push_to_database()
        # print('hello')
        # # scapojng loginc
        # url = "https://timesofindia.indiatimes.com/sports/cricket/ipl/top-stories/glenn-maxwell-opts-out-of-ipl-2026-pens-emotional-goodbye-to-fans/articleshow/125710727.cms"

        # # res = TOIPreprocessing(url)

        # with open("news.txt", "w") as file:
        #     file.write(str(res.get_meta_data()))


        # print(res.get_meta_data())
   
        # xyz = ModelHandler()
        # res = xyz.summarize_article(article=article)
        # print(f"response is {res}")
        # articles = get_articles_and_push_to_database()
        # # print(f"val is {articles[1]}")
        # for article in articles:
        #     print("*" * 200)
        #     print(article["title"])
        #     handler = TOIPreprocessing(article["link"])

        #     print("data is ", handler.get_meta_data())

        # print(f"len is {len(articles)}")


        queue = QueueHandler()

        queue.publisher("hello_queue")
    # print_hi('PyCharm')


    except Exception as e:
        # logger.error(f"error in main function: {str(e)}")
        exit(0)
    
    # print(f"database url {database_url}")

    

# 
    # sel


    
    

    # database init




# See PyCharm help at https://www.jetbrains.com/help/pycharm/
