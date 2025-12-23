import logging
from threading import Lock

import sqlalchemy
from sqlalchemy import Engine, Connection


class DBConnection:

    _engine = None

    _lock = Lock()

    @classmethod
    def init(cls, database_url: str):

        if cls._engine is not None:
            return cls._engine

        with cls._lock:
            if cls._engine is None:

                try:
                    cls._engine = sqlalchemy.create_engine(database_url)
                    logging.info("Database connection estb")
                    # return cls._engine

                except Exception as e:
                    logging.error(f"Failed to connect to db {str(e)}")

                    raise e

        return cls._engine

    @classmethod
    def get_engine(cls):

        if cls._engine is None:
            logging.info("First initilize database connection.")
            raise Exception("First initilize database connection.")

        return cls._engine

    @classmethod
    def get_connection(cls):
        if cls._engine is None:
            logging.info("first initilize database engine")

            return None

        return cls._engine.connect()
