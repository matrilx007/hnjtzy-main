import scrapy
from html2docx import html2docx
import uuid
from bs4 import BeautifulSoup
import re

class ExamSpider(scrapy.Spider):
    name = "exam"
    allowed_domains = ["jwc.hnjtzy.com.cn", "tpfj.hnjtzy.com.cn"]
    start_urls = ["https://jwc.hnjtzy.com.cn/2715/",
                  "https://jwc.hnjtzy.com.cn/2715/list-2.shtml",
                  "https://jwc.hnjtzy.com.cn/2715/list-3.shtml",
                  "https://jwc.hnjtzy.com.cn/2715/list-4.shtml",
                  "https://jwc.hnjtzy.com.cn/2715/list-5.shtml",
                  "https://jwc.hnjtzy.com.cn/2715/list-6.shtml",]

    def parse(self, response):
        urls = self.parse_urls(response)
        for url in urls:
            yield scrapy.Request(url, callback=self.parse_page)


    def parse_urls(self, response):
        urls = []
        i = 1
        link = response.xpath(f'/html/body/div[2]/div[3]/div[2]/div/div[2]/div/ul/li[{i}]/a/@href').get()
        while link:
            urls.append(link)
            i += 1
            link = response.xpath(f'/html/body/div[2]/div[3]/div[2]/div/div[2]/div/ul/li[{i}]/a/@href').get()

        return urls

    def parse_page(self, response):
        yield from self.parse_document(response)
        title = response.xpath('/html/body/div[2]/div[3]/div[2]/div/div[2]/div[1]/text()').get().strip()
        doc_html = response.xpath('/html/body/div[2]/div[3]/div[2]/div').get()
        soup = BeautifulSoup(doc_html, 'html.parser')
        for table in soup.find_all('table'):
            for row in table.find_all('tr'):
                for cell in row.find_all('td'):
                    if not cell.get_text().strip():
                        cell.string = " "
        doc_buf = html2docx(str(soup), title="文件")

        with open(title + ".docx", "wb") as f:
            f.write(doc_buf.getvalue())
        

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
        filename = filename.strip()
        with open(f'{filename}', 'wb') as f:
            f.write(response.body)

