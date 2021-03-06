# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractor import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider
from multiprocessing import Process, Queue

# scrapy api
from twisted.internet import reactor
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from scrapy.crawler import CrawlerRunner


class DatabloggerSpider(CrawlSpider):
    # The name of the spider
    name = "datablogger"

    # The domains that are allowed (links to other domains are skipped)
    allowed_domains = ["data-blogger.com"]

    # The URLs to start with
    start_urls = ["https://www.data-blogger.com/"]

    # This spider has one rule: extract all (unique and canonicalized) links, follow them and parse them using the parse_items method
    rules = [
        Rule(
            LinkExtractor(
                canonicalize=True,
                unique=True
            ),
            follow=True,
            callback="parse_items"
        )
    ]

    # Method which starts the requests by visiting all URLs specified in start_urls
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, dont_filter=True)

    # Method for parsing items
    def parse_items(self, response):
        # The list of items that are found on the particular page
        items = []
        # Only extract canonicalized and unique links (with respect to the current page)
        links = LinkExtractor(canonicalize=True, unique=True).extract_links(response)
        # Now go through all the found links
        for link in links:
            # Check whether the domain of the URL of the link is allowed; so whether it is in one of the allowed domains
            is_allowed = False
            for allowed_domain in self.allowed_domains:
                if allowed_domain in link.url:
                    is_allowed = True
            # If it is allowed, create a new item and add it to the list of found items
            if is_allowed:
                item = DatabloggerScraperItem()
                item['url_from'] = response.url
                item['url_to'] = link.url
                items.append(item)
        # Return all the found items
        return items

def run_spider(list_, max_limit=-1):
    q = Queue()
    p = Process(target=f, args=(q,list_,max_limit,))
    p.start()
    result = q.get()
    p.join()

    if result is not None:
        raise result

def f(q,list_, max_limit=-1):
    print(list_)
    print(max_limit)
    try:
        runner = CrawlerRunner()
        deferred = runner.crawl(DatabloggerSpider())
        deferred.addBoth(lambda _: reactor.stop())
        reactor.run()
        q.put(None)
    except Exception as e:
        q.put(e)

class DatabloggerScraperItem(scrapy.Item):
    # The source URL
    url_from = scrapy.Field()
    # The destination URL
    url_to = scrapy.Field()