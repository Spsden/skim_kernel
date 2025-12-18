

from abc import abstractmethod
import logging
from sqlalchemy import Engine
from database.connection import DBConnection


class RepositoryBase:

    def __init__(self) -> None:
        self.logger = logging.getLogger(f"Repository")

        # try:
        #     self.database_engine = database_engine


        # except Exception as e:

        #     self.logger.error(f"Error in Repository: {str(e)}")

    def insert(self, engine: Engine, data):            
        pass

    




    
    