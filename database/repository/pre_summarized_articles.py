



from abc import abstractmethod
import logging

from sqlalchemy import Engine
from typing import List
from sqlalchemy.orm import sessionmaker

from database.models.models import RawArticles
from database.repository.repository_base import RepositoryBase


class PresummarizedArticleRepository(RepositoryBase):

    @classmethod
    def insert(cls, engine: Engine, data: List[RawArticles]):
        """
            to insert data into database
        """
        try:
            Session = sessionmaker(engine)

            session = Session()

            session.add_all(data)

            session.commit()

            session.close()

            logging.info(f"Data sucessfully inserted into database")


        except Exception as e:
            logging.error(f"Failed to insert data into database: {str(e)}") 
            # return None

