# -*- coding: utf-8 -*-
import hashlib

import re
import scrapy
from w3lib import html
from ..utils import common
from scrapy.http import Response
from ..items import SpecificProduct
from ..logger import catch_exception_and_log


class DeyangSpiderSpider(scrapy.Spider):
    name = 'deyang_spider'
    allowed_domains = ['xxgk.deyang.gov.cn']
    start_urls = ['http://xxgk.deyang.gov.cn/xxgkml/qxindex.jsp?regionName=zjx']
    # 入库的集合
    mongo_collection = "deyang_zjx"
    # 设置每一个spider需要的中间件
    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS': 64,
        'DOWNLOADER_MIDDLEWARES': {
            'currency.middlewares.RandomUserAgentMiddleware': 543,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,  # 关闭scrapy默认UA
        }
    }

    def parse(self, response: Response):
        all_list = [
            '县财政局',
            '县人防办',
        ]

        list_href = response.xpath("//div[@id='zwgkRight']//div[4]//div[@class='bd']//table//tr//td/a")
        for i in list_href:
            department = i.xpath("./text()").get()
            href = response.urljoin(i.xpath("./@href").get())
            department_id = re.search(r"\d+", href).group()
            department_href = "http://xxgk.deyang.gov.cn/xxgkml/gklist_iframe.jsp?regionName=zjx&deptId={}".format(department_id)
            print(department)
            print(href)
            if department not in all_list:
                continue
            type_ = common.get_publisher(department)
            if not type_:
                type_ = "不分类"
            data = {"department": department, "department_id": department_id, 'type': type_}
            yield scrapy.Request(url=department_href, meta=data, callback=self.gen_list)

    def gen_list(self, response: Response):
        # 获取上层传递数据
        data = response.meta

        text = response.xpath("//p[@class='pages']").xpath("string(.)").get()
        if text:
            text = html.replace_escape_chars(text).replace(" ", "").replace("\u3000", "")

            pages: str = re.search("共(\d+)页", text).group(1)
            print("当前链接共%s页" % pages)
            for index in range(1, int(pages) + 1):
                new_url = response.url + "&pageIndex=" + str(index)
                yield scrapy.Request(url=new_url, meta=data, callback=self.parse_department)

    def parse_department(self, response: Response):
        data: dict = response.meta
        department = data.get("department")
        department_id = data.get("department_id")
        type_: str = data.get("type")

        trs = response.xpath("//div[@class='info-list']/table/tbody/tr")
        for tr in trs:
            link = response.urljoin(tr.xpath("./td[@class='tit']/a/@href").get())
            print(link)
            name = tr.xpath("./td[@class='tit']//div[@class='lay']//tr[2]/td/text()").get()

            item = SpecificProduct()
            _id = common.md5Hex(link, False)
            item['_id'] = _id
            item['department'] = department
            item['department_id'] = department_id
            item['type'] = type_
            item['link'] = link
            item['name'] = name
            item['source_url'] = response.url

            mongo_update_instruction = {
                "filter": {"_id": _id},
                "update": {
                    "$set": item.copy()
                },
                "upsert": True
            }
            item['mongo_collection'] = self.mongo_collection
            item['mongo_update_instruction'] = mongo_update_instruction

            yield item
