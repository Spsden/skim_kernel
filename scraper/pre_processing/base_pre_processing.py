from abc import abstractmethod
import logging


class BasePreProcessing:
    """
    base abstract class contains methods that need to be implemented
    """

    def __init__(self, raw_url: str) -> None:
        self.raw_url = raw_url
        self.logger = logging.getLogger(f"{self.__class__.__name__}")

    @abstractmethod
    def normal_url_to_processed(self) -> str:
        pass

    @abstractmethod
    def get_meta_data(self):
        pass

    @abstractmethod
    def get_article_body(self):
        pass
