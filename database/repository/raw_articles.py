

from abc import abstractmethod
import logging

from sqlalchemy import Engine
from typing import List
from sqlalchemy.orm import sessionmaker

from database.models.models import RawArticles
from database.repository.repository_base import RepositoryBase


class RawArticleRepository(RepositoryBase):

    @classmethod
    def insert_all(cls, engine: Engine, data: List[RawArticles]):
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

    @classmethod
    def insert(cls, engine: Engine, data: RawArticles):
        """
            to insert data into database and return id
        """
        try:
            Session = sessionmaker(engine)

            session = Session()

            session.add(data)

            session.commit()

            # session.close()

            logging.info(f"Data sucessfully inserted into database")

            return data.id

        except Exception as e:
            logging.error(f"Failed to insert data into database: {str(e)}") 
            return None

