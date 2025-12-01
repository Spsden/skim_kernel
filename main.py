# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from database.connection import DBConnection
from rss_feeds.core.aggregrator import main
from dotenv import load_dotenv
from config.env import get_env

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


load_dotenv()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    # print_hi('PyCharm')

    main()

    # database_url: str = get_env("DATABASE_URL")

    # db_engine = DBConnection.init(database_url=database_url)

    
    

    # database init




# See PyCharm help at https://www.jetbrains.com/help/pycharm/
