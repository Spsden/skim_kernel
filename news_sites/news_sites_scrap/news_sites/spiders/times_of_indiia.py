from typing import Iterable

import scrapy
from scrapy import Request


class TOISpiderSpider(scrapy.Spider):
    name = 'toi_spider'
    allowed_domains = ['timesofindia.indiatimes.com']
    start_urls = ['https://timesofindia.indiatimes.com/']

    # def start_requests(self) -> Iterable[Request]:
    #     urls = [
    #         'https://timesofindia.indiatimes.com/'
    #     ]
    #     for url in urls:
    #         yield scrapy.Request(url=url,callback=self.parse())

    def parse(self, response):
        # Extract news headlines
        headlines = response.css('h1.headline::text').getall()

        # Extract news links
        links = response.css('div.article-list > div > h2 > a::attr(href)').getall()

        # Yield items
        for headline, link in zip(headlines, links):
            yield {
                'headline': headline.strip(),
                'link': link,
            }

        # Follow pagination links
        next_page = response.css('li.next-page a::attr(href)').get()
        if next_page:
            yield scrapy.Request(url=response.urljoin(next_page), callback=self.parse)
