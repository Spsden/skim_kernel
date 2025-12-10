 # This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from dotenv.main import logger
from database.connection import DBConnection
from rss_feeds.core.aggregrator import get_articles_and_push_to_database
from dotenv import load_dotenv
from config.env import get_env
from llm_handler.model_handler import ModelHandler

load_dotenv()


if __name__ == '__main__':


    try:
        # database_url: str = get_env("DATABASE_URL")

        # db_engine = DBConnection.init(database_url=database_url)

        # get_articles_and_push_to_database()
        print('hello')

        article = """
NEW DELHI: Goa police have confirmed that Saurabh and Gaurav Luthra, owners of the Birch by Romeo Lane nightclub where a devastating fire killed 25 people, are currently in Thailand, raising the central question now driving the investigation: can the brothers be extradited? As authorities pursue them with international assistance, India’s extradition treaty with Thailand has come sharply into focus.
Interpol has issued a Blue Corner Notice against the Luthras after they fled the country within hours of the blaze. Goa’s Deputy Inspector General, Varsha Sharma, said, “We have come to know that the club owners are in Phuket, and we are taking action with the help of CBI and INTERPOL.” She added that Lookout Circulars had been issued and that “our teams are present in Delhi” as the search widened beyond India’s borders. Officials described the rapid issuance of the notice as unusually swift, adding, “Normally, this process takes a week or more, but because of the concerted efforts of Goa Police and the strong support from central agencies, it was completed much faster.”
What the treaty says

Under the extradition treaty signed between India and Thailand, both countries are obligated to surrender individuals wanted “for prosecution, trial or for the imposition or execution of punishment” for offences punishable by at least one year of imprisonment in both jurisdictions. The treaty makes clear that the categorisation or terminology of an offence does not have to match in both legal systems, and that extradition can also be granted in cases of attempts, aiding or abetting, or participation as an accomplice. If the offence was committed outside India, extradition may still be granted if Thailand’s laws allow similar prosecution, and even when they do not, the treaty permits Thailand to exercise discretion to extradite.
There are also mandatory grounds on which a request can be rejected, including if the case is judged to be politically motivated or if prosecution is barred by lapse of time. Neither appears relevant to the nightclub fire, which police say killed 20 staff members and five tourists, including four from Delhi. Thailand also retains the right to refuse extradition of its own nationals, but the Luthras are Indian citizens, a factor that strengthens India’s position.
The fire broke out in the early hours of Sunday in Arpora, triggering a high-casualty incident that state officials have described as “very painful.” Sharma said, “The accused were immediately charged and arrested. We took immediate action against the owners by issuing LOC against them.” A co-owner, Ajay Gupta, has also been named among the accused and is now on a Lookout Circular. Another owner, Surinder Kumar Khosla, a British national, is also wanted.


Meanwhile, the fallout has triggered action on the ground in Goa. Part of the Romeo Lane restaurant at Vagator—another establishment tied to the Luthra-owned chain—was demolished earlier today for beach encroachment. Deputy Director of Tourism Dhiraj Wagale said, “The total area to be demolished is 198 square metres,” adding that the owners had rebuilt the structure after an earlier demolition in July."""

        xyz = ModelHandler()
        xyz.summarize_article(article=article)
    # print_hi('PyCharm')
    except Exception as e:
        logger.error(f"error in main function: {str(e)}")
        exit(0)
    
    # print(f"database url {database_url}")

    

# 
    # sel


    
    

    # database init




# See PyCharm help at https://www.jetbrains.com/help/pycharm/
