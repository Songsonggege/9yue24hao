# -*- coding: utf-8 -*-
import scrapy


class HttpbinSpider(scrapy.Spider):
    name = 'httpbin'
    # allowed_domains = ['http://www.httpbin.org']
    start_urls = ['http://www.httpbin.org/get']
    def parse(self, response):
        print(response.text)
