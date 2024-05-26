import requests
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from extractPage import ExtraxtPage

class Crawling(CrawlSpider):
    name = "mycrawler"
    handle_httpstatus_list = [999]
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "accept-encoding": "gzip, deflate, sdch, br",
        "accept-language": "en-US,en;q=0.8,ms;q=0.6",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
    }

    rules = [
        Rule(LinkExtractor(allow="company/", unique=True), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow="profile/", unique=True), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow="browsecompanies.html", unique=True), callback='parse_item', follow=True),
        Rule(LinkExtractor(unique=True), callback='parse_item', follow=True),
    ]

    def __init__(self, seeds=None, *args, **kwargs):
        super(Crawling, self).__init__(*args, **kwargs)
        self.start_urls = seeds

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        spider.settings.set(
            "DEPTH_LIMIT", 3, priority="spider"
        )
        return spider

    def parse_item(self, response):
        isSeed = 0

        if response.url in self.start_urls:
            isSeed = 1

        extractPage = ExtraxtPage(response)
        extractPage.process(isSeed)