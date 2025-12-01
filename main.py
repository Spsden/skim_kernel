# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from dotenv.main import logger
from database.connection import DBConnection
from rss_feeds.core.aggregrator import get_articles_and_push_to_database
from dotenv import load_dotenv
from config.env import get_env


load_dotenv()


if __name__ == '__main__':


    try:
        database_url: str = get_env("DATABASE_URL")

        db_engine = DBConnection.init(database_url=database_url)

        get_articles_and_push_to_database()

    # print_hi('PyCharm')
    except Exception as e:
        logger.error(f"error in main function: {str(e)}")
        exit(0)
    
    print(f"database url {database_url}")

    

# 
    # 


    
    

    # database init




# See PyCharm help at https://www.jetbrains.com/help/pycharm/
