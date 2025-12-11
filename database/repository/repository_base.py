

from abc import abstractmethod

from sqlalchemy import Engine


class RepositoryBase:

    @abstractmethod
    # @classmethod
    def insert(cls, engine: Engine, data):
        pass

    




    
    