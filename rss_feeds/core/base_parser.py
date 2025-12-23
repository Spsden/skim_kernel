from abc import ABC, abstractmethod
import xml.etree.ElementTree as et
from datetime import datetime
import logging
import re
from typing import List, Dict, Optional, Any
from urllib.parse import urlparse
import html
import requests


class BaseNewsFeedParser(ABC):

    def __init__(self, feed_url: str, source_name: str):
        self.feed_url = feed_url
        self.source_name = source_name
        self.logger = logging.getLogger(f"{self.__class__.__name__}_{source_name}")

        self.config = {
            "max_description_length": 500,
            "validate_urls": True,
            "extract_images": True,
        }

    @abstractmethod
    def _parse_specific_feed(self, root: et.Element) -> List[Dict[str, Any]]:
        pass

    def parse_feed(self) -> List[Dict[str, Any]]:
        try:
            response = requests.get(
                self.feed_url,
                timeout=10,
                ##TODO : FIND SUITABLE HEADERS. FIREFOX HEADERS BREAK TOI
                # headers={
                #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0',
                #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                #     'Accept-Encoding': 'gzip, deflate, br',
                #     'Accept-Language': 'en-US,en;q=0.9',
                #     'Connection': 'keep-alive',
                #     'Upgrade-Insecure-Requests': '1',
                #     'TE': 'Trailers'
                # }
            )
            response.raise_for_status()
            self.logger.info(
                f"Response received from : {self.source_name}  {self.feed_url}"
            )
            try:
                root = et.fromstring(response.content)
            except et.ParseError as xml_err:
                self.logger.error(f"XML Parsing error: {xml_err}")
                with open("error_feed.xml", "wb") as f:
                    f.write(response.content)
                raise

            articles = self._parse_specific_feed(root)

            articles = self._post_process_articles(articles)

            return articles

        except requests.RequestException as req_err:
            self.logger.error(
                f"Network error fetching {self.source_name} feed: {req_err}"
            )
            raise
        except Exception as e:
            self.logger.error(
                f"Unexpected error processing {self.source_name} feed: {e}"
            )
            raise

    def _post_process_articles(
        self, articles: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        processed_articles = []
        for article in articles:
            article["source"] = self.source_name

            if (
                article.get("description")
                and len(article["description"]) > self.config["max_description_length"]
            ):
                article["description"] = (
                    article["description"][: self.config["max_description_length"]]
                    + "..."
                )

            if self.config["validate_urls"]:
                if not self._validate_url(article.get("link", "")):
                    self.logger.warning(f"Invalid article URL: {article.get('link')}")
                    continue

            processed_articles.append(article)

        return processed_articles

    @staticmethod
    def _validate_url(url: str) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

    @staticmethod
    def _clean_html(text: Optional[str], strip_tags: bool = True) -> str:
        if not text:
            return ""

        text = html.unescape(text)
        text = text.replace("<![CDATA[", "").replace("]]>", "")
        if strip_tags:
            text = re.sub(r"<[^>]+>", "", text)
        text = " ".join(text.split())

        return text.strip()

    @staticmethod
    def _parse_datetime(
        date_str: Optional[str], formats: List[str] = None
    ) -> Optional[str]:
        if not date_str:
            return None

        default_formats = [
            "%a, %d %b %Y %H:%M:%S %z",
            "%Y-%m-%d %H:%M:%S %z",
            "%Y-%m-%dT%H:%M:%S%z",
        ]

        formats = formats or default_formats

        for fmt in formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.isoformat()
            except (ValueError, TypeError):
                continue

        logging.warning(f"Could not parse date: {date_str}")
        return None

    @abstractmethod
    def extract_image_url(self, item) -> Optional[str]:
        pass

    @abstractmethod
    def get_articles(self):
        pass
