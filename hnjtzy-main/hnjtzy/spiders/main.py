import scrapy


class MainSpider(scrapy.Spider):
    name = "main"
    allowed_domains = ["jwc.hnjtzy.com.cn"]
    start_urls = ["https://jwc.hnjtzy.com.cn"]

    def parse(self, response):
        pass
