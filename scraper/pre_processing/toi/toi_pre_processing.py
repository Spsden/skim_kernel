from abc import abstractmethod
import datetime
import json
import logging
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import requests

# from scraper.pre_processing.base_pre_processing import BasePreProcessing
import re
from urllib.parse import urlparse, urlunparse


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


class TOIPreprocessing(BasePreProcessing):
    """
    scraping logic for TOI
    """

    def __init__(self, raw_url: str) -> None:
        super().__init__(raw_url)

    def normal_url_to_processed(self) -> str:
        """
        convert 'articleshow/' to 'articleshowprint/'.
        """
        parsed = urlparse(self.raw_url)

        path_parts = parsed.path.split("/")

        new_parts = []
        replaced = False
        for part in path_parts:
            if part == "articleshow":
                new_parts.append("articleshowprint")
                replaced = True
            else:
                new_parts.append(part)
        if replaced:
            new_path = "/".join(new_parts)
            new_parsed = parsed._replace(path=new_path)
            return urlunparse(new_parsed)
        else:
            return url

    def extract_body_print(self):

        try:
            # print article url for body extraction
            modified_url = self.normal_url_to_processed()

            resp = requests.get(modified_url, headers={"User-Agent": "Mozilla/5.0"})

            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            paragraphs = soup.find_all("div", {"class": "Normal"})
            body = []

            for p in paragraphs:
                text = p.get_text(strip=True)
                if text:
                    body.append(text)

            return "\n\n".join(body) if body else None
        except Exception as e:
            self.logger.error(f"Failed to extract body {str(e)}")

    def normalize_date(self, raw_date: str):

        if not raw_date:
            return None

        raw = raw_date.replace("IST", "").strip()

        # "Dec 02, 2025, 00:48" format
        try:
            dt = datetime.strptime(raw, "%b %d, %Y, %H:%M")

            return dt.isoformat()

        except:
            pass

        # iso
        try:
            dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))

            return dt.isoformat()
        except:
            return raw_date

    def get_article_data(self) -> Dict[str, Any]:

        try:
            # invoke call
            resp = requests.get(self.raw_url, headers={"User-Agent": "Mozilla/5.0"})

            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, "html.parser")

            # title handler
            title: str

            if soup.find("h1"):
                title = soup.find("h1").get_text(strip=True)

            elif soup.title:
                title = soup.title.get_text(strip=True)

            # author / authors and publish date
            authors = []
            published_date = None

            # article text contains date + authors
            meta_text = soup.find(string=re.compile(r"Updated:|Published:", re.I))

            if meta_text:
                text = meta_text.strip()

                # Extract authors
                parts = [p.strip() for p in text.split("/") if p.strip()]

                if len(parts) >= 2:
                    authors = parts[:-1]

                # Extract date
                m = re.search(r"(Published|Updated):\s*(.*)", text)
                if m:
                    published_date = self.normalize_date(m.group(2))

            # description
            description = None

            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc:

                description = meta_desc.get("content")

            if not description:

                sub = soup.find("h2")

                if sub:
                    description = sub.get_text(strip=True)

            scripts = soup.find_all("script", type="application/ld+json")
            for sc in scripts:
                try:
                    data = json.loads(sc.string)

                    blocks = data if isinstance(data, list) else [data]

                    for block in blocks:
                        if not isinstance(block, dict):
                            continue

                        if "datePublished" in block:
                            published_date = published_date or self.normalize_date(
                                block["datePublished"]
                            )

                        if "author" in block:
                            auth = block["author"]

                            if isinstance(auth, dict) and auth.get("name"):
                                authors.append(auth["name"])

                            elif isinstance(auth, list):
                                for a in auth:
                                    if isinstance(a, dict) and a.get("name"):
                                        authors.append(a["name"])

                except:
                    pass

            body = self.extract_body_print()

            authors = list(dict.fromkeys(authors))

            return {
                "title": title or None,
                "description": description or None,
                # "authors": authors or None,
                "authors": None,
                "published_date": published_date or None,
                "body": body or None,
            }

        except Exception as e:
            self.logger.error(f"Error in getting meta data {str(e)}")
            return None


if __name__ == "__main__":

    url = "https://timesofindia.indiatimes.com/sports/cricket/ipl/top-stories/glenn-maxwell-opts-out-of-ipl-2026-pens-emotional-goodbye-to-fans/articleshow/125710727.cms"

    # res = TOIPreprocessing(url)

    # with open("news.txt", "w") as file:
    #     file.write(str(res.get_meta_data()))

    # print(res.get_meta_data())
