import requests
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup


class NewsScraper(ABC):

    def __init__(self, url):
        self.url = url
        self.html_content = None
        self.soup = None

    def fetch_content(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            self.html_content = response.text
            self.soup = BeautifulSoup(self.html_content, "html.parser")
        else:
            raise Exception(
                f"Failed to fetch the page. Status code: {response.status_code}"
            )

    @abstractmethod
    def parse_title(self):
        pass

    @abstractmethod
    def parse_content(self):
        pass

    def get_article_data(self):
        if self.html_content is None:
            self.fetch_content()
        title = self.parse_title()
        content = self.parse_content()
        return {"title": title, "content": content}


class BBCCrawler(NewsScraper):

    def parse_title(self):
        """Parse the article title for BBC."""
        title_tag = self.soup.find("h1", {"class": "story-headline"})
        if title_tag:
            return title_tag.get_text(strip=True)
        return None

    def parse_content(self):
        """Parse the article content for BBC."""
        paragraphs = self.soup.find_all("p", {"class": "story-body__introduction"})
        content = " ".join([para.get_text(strip=True) for para in paragraphs])
        return content


class TOICrawler(NewsScraper):

    def parse_title(self):
        """Parse the article title for TOI."""
        title_tag = self.soup.find("h1", {"class": "title"})
        if title_tag:
            return title_tag.get_text(strip=True)
        return None

    def parse_content(self):
        """Parse the article content for TOI."""
        paragraphs = self.soup.find_all("div", {"class": "Normal"})
        content = " ".join([para.get_text(strip=True) for para in paragraphs])
        return content


class IndiaTimesCrawler(NewsScraper):

    def parse_title(self):
        """Parse the article title for India Times."""
        title_tag = self.soup.find("h1", {"class": "heading1"})
        if title_tag:
            return title_tag.get_text(strip=True)
        return None

    def parse_content(self):
        """Parse the article content for India Times."""
        paragraphs = self.soup.find_all("p", {"class": "p-text"})
        content = " ".join([para.get_text(strip=True) for para in paragraphs])
        return content


def create_scraper(url):
    if "bbc.co.uk" in url:
        return BBCCrawler(url)
    elif "timesofindia.indiatimes.com" in url:
        return TOICrawler(url)
    elif "indiatimes.com" in url:
        return IndiaTimesCrawler(url)
    else:
        raise ValueError("Unsupported website")


if __name__ == "__main__":
    url = "https://www.bbc.co.uk/news/article"

    scraper = create_scraper(url)
    article_data = scraper.get_article_data()

    print(f"Title: {article_data['title']}")
    print(
        f"Content: {article_data['content'][:200]}..."
    )  # Printing first 200 characters of content
