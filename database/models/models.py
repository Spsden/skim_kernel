from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Boolean
from sqlalchemy.sql.functions import func

from database.table_names import TABLES

Base = declarative_base()
metadata = Base.metadata

class RawArticles(Base):

    __tablename__ = TABLES["raw_articles"]

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    title = Column(String, nullable=False)

    article_url = Column(String, nullable=False)

    source = Column(String, nullable=False)

    image_url = Column(String, nullable=False)

    processed = Column(Boolean, default=False)

    published_date = Column(String, nullable=False)

    createdAt = Column(DateTime, nullable=False, insert_default=func.now())

    updatedAt = Column(DateTime, nullable=False, insert_default=func.now(), onupdate=func.now())


class SummarizedArticles(Base):

    __tablename__ = TABLES["summarized_articles"]

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    updated_title = Column(String, nullable=False)

    src_url = Column(String, nullable=False)

    body = Column(String, nullable=False)

    img_src = Column(String, nullable=False)

    createdAt = Column(DateTime, nullable=False, insert_default=func.now())

    updatedAt = Column(DateTime, nullable=False, insert_default=func.now(), onupdate=func.now())


class ArticlesCategory(Base):

    __tablename__ = TABLES["article_category"]

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    name = Column(String, nullable=False)

    logo_src = Column(String, nullable=False)

    description = Column(String, nullable=False)

    created_at = Column(DateTime, nullable=False, insert_default=func.now())

    updatedAt = Column(DateTime, nullable=False, insert_default=func.now(), onupdate=func.now())