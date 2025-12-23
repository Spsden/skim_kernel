from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Boolean
from sqlalchemy.sql.functions import func
from sqlalchemy.orm import relationship

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

    updatedAt = Column(
        DateTime, nullable=False, insert_default=func.now(), onupdate=func.now()
    )

    summary = relationship(
        "SummarizedArticles",
        uselist=False,
        back_populates="raw_article",
        cascade="all, delete-orphan",
    )


class SummarizedArticles(Base):

    __tablename__ = TABLES["summarized_articles"]

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    title = Column(String, nullable=False)

    article_url = Column(String, nullable=False)

    source = Column(String, nullable=False)

    body = Column(String, nullable=True)

    img_src = Column(String)

    published_date = Column(String)

    createdAt = Column(DateTime, nullable=False, insert_default=func.now())

    updatedAt = Column(
        DateTime, nullable=False, insert_default=func.now(), onupdate=func.now()
    )

    category = relationship("ArticlesCategory", back_populates="articles")
    category_id = Column(Integer(), ForeignKey(f"{TABLES['article_category']}.id"))

    raw_article = relationship("RawArticles", back_populates="summary", uselist=False)
    raw_article_id = Column(
        Integer(), ForeignKey(f"{TABLES['raw_articles']}.id"), unique=True
    )


class ArticlesCategory(Base):

    __tablename__ = TABLES["article_category"]

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    name = Column(String, nullable=False)

    logo_src = Column(String, nullable=False)

    description = Column(String, nullable=False)

    created_at = Column(DateTime, nullable=False, insert_default=func.now())

    updatedAt = Column(
        DateTime, nullable=False, insert_default=func.now(), onupdate=func.now()
    )

    articles = relationship("SummarizedArticles", back_populates="category")
