from abc import abstractmethod
import logging

from sqlalchemy import Engine, update
from typing import List
from sqlalchemy.orm import sessionmaker

from database.models.models import SummarizedArticles
from database.repository.repository_base import RepositoryBase


class PresummarizedArticleRepository(RepositoryBase):

    @classmethod
    def insert_all(cls, engine: Engine, data: List[SummarizedArticles]):
        """
        to insert data in batches into database
        """
        try:
            Session = sessionmaker(engine)

            session = Session()

            session.add_all(data)

            session.commit()

            session.close()

            logging.info(f"Data sucessfully inserted into database")

        except Exception as e:
            logging.error(f"Failed to insert: {str(e)}")
            # return None

    @classmethod
    def insert(cls, engine: Engine, data: SummarizedArticles):
        """
        to insert one record at a time and return back the id
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
            logging.error(f"Failed to insert: {str(e)}")
            return None

    @classmethod
    def update_body(cls, id, engine: Engine, article_body: str):
        try:
            Session = sessionmaker(engine)

            session = Session()

            article_to_update = (
                session.query(SummarizedArticles).filter_by(id=id).first()
            )

            if article_to_update is None:
                logging.warning(f"Article with {id} not found")
                return

            article_to_update.body = article_body  # type: ignore
            session.commit()

            logging.info(f"Article {id} body is updated.")

        except Exception as e:
            logging.error(f"Failed to update: {str(e)}")
