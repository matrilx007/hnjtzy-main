import scrapy
from html2docx import html2docx
import uuid
from bs4 import BeautifulSoup
import re

class DocumentSpider(scrapy.Spider):
    name = "document"
    allowed_domains = ["jwc.hnjtzy.com.cn", "tpfj.hnjtzy.com.cn"]
    start_urls = ["https://jwc.hnjtzy.com.cn/6963", "https://jwc.hnjtzy.com.cn/6963/list-2.shtml"]

    def parse(self, response):
        urls = self.parse_urls(response)
        for url in urls:
            link = url.xpath('@href').get()
            if "xlsx" in link or "xls" in link:
                title = url.xpath('normalize-space(.)').get() + '.' + link.split('.')[-1]
                link = response.urljoin(link)
                yield scrapy.Request(link, 
                                callback=self.parse_page_by_document,
                                meta={'filename': title})
            else:
                yield scrapy.Request(link, callback=self.parse_page)

    def parse_urls(self, response):
        urls = []
        i = 1
        url = response.xpath(f'/html/body/div[2]/div[3]/div[2]/div/div[2]/div/ul/li[{i}]/a')
        while url:
            urls.append(url)
            i += 1
            url = response.xpath(f'/html/body/div[2]/div[3]/div[2]/div/div[2]/div/ul/li[{i}]/a')

        return urls
    
    def parse_page(self, response):
        yield from self.parse_document(response)
    
    def parse_document(self, response):
        doc_links = response.xpath('//a[contains(@href, ".doc") or contains(@href, ".docx") or contains(@href, ".pdf") or contains(@href, ".xlsx") or contains(@href, ".xls")]')
        for link in doc_links:
            absolute_url = response.urljoin(link.xpath('@href').extract_first())
            title = link.xpath('normalize-space(.)').extract_first()
            if title == "":
                title = link.xpath('@title').get()
            if title == "":
                continue
            yield scrapy.Request(absolute_url, 
                                callback=self.download_document,
                                meta={'filename': title})

    def download_document(self, response):
        filename = response.meta.get('filename') or response.url.split('/')[-1]
        filename = "".join(c for c in filename if c.isalnum() or c in (' ', '.', '_', '-')).rstrip()
        with open(f'{filename}', 'wb') as f:
            f.write(response.body)

    def parse_page_by_document(self, response):
        filename = response.meta.get('filename') or response.url.split('/')[-1]
        filename = "".join(c for c in filename if c.isalnum() or c in (' ', '.', '_', '-')).rstrip()
        with open(f'{filename}', 'wb') as f:
            f.write(response.body)  