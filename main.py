import json
from scrapy.crawler import CrawlerProcess
from crawler.crawler.spiders.firstCrawler import Crawling

async def run_crawler():
    #open config file
    file = open('config.json')
    config = json.load(file)

    #get seeds url
    seeds = config['seeds']

    #start crawler
    process = CrawlerProcess(settings={
        'FEED_FORMAT': 'json',
        'COOKIES_ENABLED': 'False',
        'COOKIES_DEBUG': 'True',
        'DOWNLOAD_DELAY': 3,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0'
    })
    process.crawl(Crawling, seeds=seeds)
    process.start()