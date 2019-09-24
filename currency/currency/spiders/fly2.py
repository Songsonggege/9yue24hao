# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Response


class Fly2Spider(scrapy.Spider):
    name = 'fly2'
    allowed_domains = ['www.creditchina.gov.cn']
    start_urls = ['https://www.creditchina.gov.cn/xinxigongshi/shipinanquanjianduchoujian/']

    # 入库的集合
    mongo_collection = "CFXK-ZYZ-0412-014"
    # 设置每一个spider需要的中间件
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'currency.middlewares.RandomUserAgentMiddleware': 543,
            'currency.middlewares.SeleniumMiddleware': 560,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,  # 关闭scrapy默认UA
        }
    }

    # def start_requests(self):
    #     # 14847
    #     target_url = 'https://www.creditchina.gov.cn/xinxigongshi/shipinanquanjianduchoujian/#page-{}'
    #     for i in range(1, 10):
    #         yield scrapy.Request(target_url.format(i), callback=self.parse)

    def parse(self, response: Response):
        lis = response.xpath("//ul[@id='search-result-list']//li")
        for li in lis:
            name = li.xpath(".//h4[@class='conpany-name']/text()").get()
            print(name)
