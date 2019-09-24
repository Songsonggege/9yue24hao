# -*- coding: utf-8 -*-
import re

import scrapy
from ..items import SfpmItem

from pm.common import deal_date, sales_status1, type1


class PaimaiSpider(scrapy.Spider):
    name = 'paimai'
    allowed_domains = ['http://s.gpai.net']
    url_set = 'http://s.gpai.net/sf/search.do?action=selloff&at={}&restate={}'
    selloff = [376, 381, 372, 378, 383, 377, 380, 385, 386, 379, ]
    url_fy = url_set + "&Page={}"
    offset = 1

    # 376,房产，381，土地，372，股权，378,机动车，383，船舶，377，物资，380，工艺品
    # 385，无形资产，382，财产性权益，386，林权矿权，379

    def start_requests(self):
        for i in self.selloff:
            for p in range(1, 5, 1):
                yield scrapy.Request(url=self.url_set.format(i, p))

    def parse(self, response):
        # print(response.text)
        u = response.url
        sales_status_url = re.findall(".*restate=(.*)", u)[0]
        sales_status = sales_status1(sales_status_url)
        type_url = re.findall(".*at=(.*)&restate=", u)[0]
        type = type1(type_url)
        type_url = re.findall(".*at=(.*)&restate=", u)[0]
        lis = response.xpath("//ul[@class = 'main-col-list clearfix']//li")
        if type_url == 1:
            for li in lis:
                # 首页图片地址
                img_src = li.xpath("./div/a/img/@src").get()
                # 详情 页url
                url = li.xpath("./div[@class = 'list-item']/div[@class = 'item-tit']/a/@href").get()
                # 源网站
                name = li.xpath("./div[@class = 'list-item']/div[@class = 'item-tit']/a/text()").get()
                # 起拍价
                currentprice = li.xpath(".//div[@class ='gpai-infos']//p[2]/b/text()").get() + li.xpath(
                    ".//div[@class ='gpai-infos']//p[2]/span[2]/text()").get()
                # 评估价
                evaluationprice = li.xpath(".//div[@class ='gpai-infos']//p[4]/span[2]").xpath("string(.)").get()
                # 竞拍开始时间
                startDate = deal_date(
                    li.xpath(".//div[@class ='gpai-infos']//p[5]/span").xpath("string(.)").get().split(" ")[0].split(
                        "：")[1])

                yield scrapy.Request(url, callback=self.prase_details,
                                     meta={'img_src': img_src, 'url': url, 'name': name, "currentprice": currentprice,
                                           "evaluationprice": evaluationprice, "startDate": startDate},
                                     dont_filter=True)
        elif type_url == 2:
            pass

        elif type_url == 3:
            pass

        elif type_url == 4:
            pass

        # 下一页
        page_html = response.xpath("//span[@class = 'page-infos']/label/text()").get()
        page_count = re.findall("共(.*)页", page_html)[0]
        # print(pages)
        for i in range(1, int(page_count) + 1):
            if self.offset < int(str(page_count)):
                self.offset += 1
                url0 = self.url_fy.format(str(self.offset))
                yield scrapy.Request(url0, callback=self.parse, )  # dont_filter=True

        pass

    def prase_details(self, response):
        item = SfpmItem()
        img_src = response.meta.get('img_src').strip()
        url = response.meta.get('url')
        name = response.meta.get('name')
        currentprice = response.meta.get('currentprice')
        evaluationprice = response.meta.get('evaluationprice')
        startDate = response.meta.get('startDate')
        pass
        # 详情页解析
