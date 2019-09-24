# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Response


class FlySpider(scrapy.Spider):
    name = 'fly'
    allowed_domains = ['www.nmpa.gov.cn']
    start_urls = ['http://www.nmpa.gov.cn/WS04/CL2065/index.html']

    # 入库的集合
    mongo_collection = "CFXK-ZYZ-0412-014"
    # 设置每一个spider需要的中间件
    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        'DOWNLOADER_MIDDLEWARES': {
            'currency.middlewares.RandomUserAgentMiddleware': 543,
            'currency.middlewares.SeleniumMiddleware': 560,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,  # 关闭scrapy默认UA
        }
    }

    def start_requests(self):
        url = "http://www.nmpa.gov.cn/WS04/CL2065/index.html"
        target_url = 'http://www.nmpa.gov.cn/WS04/CL2065/index_{}.html'
        yield scrapy.Request(url, callback=self.parse)

        for i in range(1, 8):
            yield scrapy.Request(target_url.format(i), callback=self.parse)

    def parse(self, response: Response):
        trs = response.xpath("//td[@class='2016_erji_content']//table[1]/tbody/tr")
        for temp in trs:
            link = response.urljoin(temp.xpath("./td[1]/a/@href").get())
            title = temp.xpath("string(./td[1]/a//text())").get()
            print(link)
            print(title)

