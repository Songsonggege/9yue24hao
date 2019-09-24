# -*- coding: utf-8 -*-
import hashlib
import re
import time
import pymongo
import scrapy
from ..common import extract_table_new, get_table_info
import json
from datetime import datetime
from ..items import RmfyzcsswItem
from ..tools import get_date, get_paragraph, time_offset, get_id
import random
import requests
from ..settings import DEFAULT_REQUEST_HEADERS
from lxml import etree


class SfpmSpider(scrapy.Spider):
    name = 'sfpm'
    allowed_domains = ['rmfysszc.gov.cn']

    def start_requests(self):
        url = 'https://www1.rmfysszc.gov.cn/ProjectHandle.shtml/'
        for i in range(1, 6):

            form_data = {
                "type": "0",
                "name": "",
                "city": "不限",
                "city1": "----",
                "city2": "----",
                "area": "",
                "state": "{}".format(i),
                "time": "0",
                "time1": "",
                "time2": "",
                "money": "",
                "money1": "",
                "number": "0",
                "fid1": " ",
                "fid2": " ",
                "fid3": " ",
                "order": "0",
                "page": "1",
                "include": "0"
            }

            html = requests.post(url=url, data=form_data, headers=DEFAULT_REQUEST_HEADERS,
                                 timeout=None).text

            try:
                num = int(re.findall("onclick='post\((\d+)\)'", html)[-1])
            except:
                num = 1
            if num >= 50:
                num = 50
            page = 1
            for _ in range(num):
                form_data = {
                    "type": "0",
                    "name": "",
                    "city": "不限",
                    "city1": "----",
                    "city2": "----",
                    "area": "",
                    "state": "{}".format(i),
                    "time": "0",
                    "time1": "",
                    "time2": "",
                    "money": "",
                    "money1": "",
                    "number": "0",
                    "fid1": " ",
                    "fid2": " ",
                    "fid3": " ",
                    "order": "0",
                    "page": "{}".format(page),
                    "include": "0"
                }
                page += 1

                yield scrapy.FormRequest(url=url, formdata=form_data, callback=self.parse_url,
                                         dont_filter=True, meta={"status": i})
                #     yield scrapy.FormRequest(url=url, callback=self.parse_page, meta={"status": 4})

    def parse_url(self, response):
        url_list = response.xpath('//div[@class="p_img"]/a/@href').extract()
        # price_list = response.xpath("//p[@class='prod-price']").xpath("string(.)").extract()
        for base_url in url_list:
            base_url = re.search("\d+\.shtml", base_url).group()
            url = "https://www.rmfysszc.gov.cn/statichtml/rm_obj/" + base_url

            yield scrapy.Request(url=url, callback=self.parse_page,
                                 meta={"base_url": base_url, "status": response.meta["status"]}, dont_filter=True)

    def parse_page(self, response):
        item = RmfyzcsswItem()
        # 主键
        item["uid"] = get_id.get_id(response.url)
        # 源网址
        item["url"] = response.url
        # 竞买公告
        item["announcement"] = [
            get_paragraph.get_paragraph(response.xpath('//div[@id="pmgg"]/div/p').xpath("string(.)").extract())]
        # 起拍价
        item["starting_price"] = response.xpath('//*[@id="price"]/div[1]/span/text()').extract_first()
        # 处置单位
        item["disposalunit"] = response.xpath('//div[@id="bg1"]/div[2]//span/text()').extract_first().split(":")[1]
        # 竞买须知
        item["bidding_instructions"] = [
            get_paragraph.get_paragraph(response.xpath('//*[@id="jmxz"]//p').xpath("string(.)").extract())]

        try:
            # 竞拍开始时间
            item["start_date"] = re.search("于(\d{0,4}年?\d{1,3}月\d{1,3}日上?午?\d+时?：?:?\d{0,2}分?)",
                                           item["bidding_instructions"][0]).group(1)
        except:
            # 竞拍开始时间
            item["start_date"] = ""
        if item["start_date"] == "":
            try:
                item["start_date"] = re.search("于(\d{0,4}年?\d{1,3}月\d{1,3}日上?午?\d+时?：?:?\d{0,2}分?)",
                                               item["announcement"][0]).group(1)
            except:
                # 竞拍开始时间
                item["start_date"] = ""
        try:
            # 竞拍结束时间
            item["end_date"] = re.search("至(\d{0,4}年?\d{1,3}月\d{1,3}日上?午?\d+时?：?:?\d{0,2}分?)",
                                         item["bidding_instructions"][0]).group(1)

        except:
            # 竞拍结束时间
            item["end_date"] = ""
        if item["end_date"] == "":
            try:
                item["end_date"] = re.search("至(\d{0,4}年?\d{1,3}月\d{1,3}日上?午?\d+时?：?:?\d{0,2}分?)",
                                             item["announcement"][0]).group(1)
            except:
                # 竞拍结束时间
                item["end_date"] = ""
        # 评估价
        item["evaluationprice"] = response.xpath('//*[@id="bg1"]/div[1]/table/tr[1]/td/span[2]/text()').extract_first()
        # 标的物详情
        item["introduction"] = [
            get_paragraph.get_paragraph(response.xpath('//*[@id="bdjs11"]//p').xpath("string(.)").extract())]
        # 附件下载
        file_name = response.xpath('//div[@style="text-align:left;"]/text()').extract_first()
        item["file"] = response.xpath('//div[@style="text-align:left;"]/a/@href').extract()
        # for file_u in item['file']:
        #     try:
        #         m = hashlib.md5()
        #         m.update(file_u.encode('utf-8'))
        #         url_md5 = m.hexdigest()
        #         # print(url_md5, 111)
        #         hdfs_url = "http://172.16.20.2:50070/webhdfs/v1/sites/www.rmfysszc.gov.cn/{}/?op=CREATE&overwrite=true&user.name=hdfs".format(
        #             url_md5)
        #         resp = requests.put(hdfs_url, allow_redirects=False, timeout=60)
        #         url_location = resp.headers['Location'].replace(
        #             re.findall('http://(.*?)/', resp.headers['Location'])[0], '172.16.20.2:50075')
        #         file_resp = requests.get(file_u, timeout=60)
        #         resp = requests.put(url_location, data=file_resp.content, timeout=60)
        #         if resp.status_code == 201 and resp.headers['Content-Length'] == '0':
        #             print(file_u, '上传成功！！！')
        #         else:
        #             print("上传失败!!!")
        #     except:
        #         print("没有附件")
        # 标题
        item["name"] = response.xpath('//div[@id="Title"]/h1/text()').extract_first()
        # 标的物所有人
        item["relation"] = [
            response.xpath('//*[@id="bg1"]/div[2]/table/tr[2]/td/span/text()').extract_first().split(":")[1]]
        # 标的物类型
        item["type"] = response.xpath('//*[@id="bdjs11"]/table/tr[2]/td[4]/text()').extract_first()
        # 当前价
        if response.meta["status"] == 2 or response.meta["status"] == 3 or response.meta["status"] == 5:
            item["current_price"] = item["starting_price"]
        else:
            pid = re.findall("var pid = '(\d+)'", response.body.decode("utf-8"))[2]
            oid = re.findall("var oid = '(\d+)'", response.body.decode("utf-8"))[0]
            _ = int(round(time.time() * 1000))
            data = {
                "pid": pid,
                "oid": oid,
                "_": str(_)
            }
            isRegist_url = 'https://www1.rmfysszc.gov.cn/Object/Finish.shtml'
            isRegist = requests.get(url=isRegist_url, params=data, headers=DEFAULT_REQUEST_HEADERS)
            try:
                price = re.search(r"price:'(.*?)'", isRegist.text).group(1)
                item["current_price"] = price + "万元"
            except:
                item["current_price"] = item["starting_price"]

        # 拍品状态
        if response.meta["status"] == 1:
            item["sales_status"] = "进行中"
        elif response.meta["status"] == 2:
            item["sales_status"] = "即将开始"
        elif response.meta["status"] == 3:
            item["sales_status"] = "中止暂缓撤回"
        elif response.meta["status"] == 4:
            item["sales_status"] = "成交"
        elif response.meta["status"] == 5:
            item["sales_status"] = "流标"
        else:
            item["sales_status"] = ""
        # 拍卖阶段
        item["auction_phase"] = \
            response.xpath('//*[@id="bg1"]/div[1]/table/tr[4]/td/span/text()').extract_first().split(":")[1]
        # 加价幅度
        try:
            mark_up = re.search("幅度\D(\d{0,7}.{0,5}元)", item["announcement"][0]).group(1)
            item["mark_up"] = mark_up
        except:
            item["mark_up"] = ""
        # 保证金
        item["deposits"] = response.xpath('//*[@id="bg1"]/div[1]/table/tr[2]/td/span[2]/text()').extract_first()
        # 延时周期
        item["delay_period"] = "5分钟"
        if response.meta["status"] == 1 or response.meta["status"] == 4:
            # 出价记录
            record_url = "https://www1.rmfysszc.gov.cn/object/Record/" + response.url.split("/")[-1]
            try:
                html = requests.get(url=record_url, headers=DEFAULT_REQUEST_HEADERS, timeout=100).text
                base_list = etree.HTML(html)
                record_list = base_list.xpath('//*[@id="Record"]//tr[position()>1]')
                bidding_record = []
                for record in record_list:
                    dict1 = {}
                    list = record.xpath("./td//text()")
                    # 出价状态
                    dict1["offer_state"] = list[1]
                    # 价格
                    dict1["price"] = list[3]
                    # 竞拍人
                    dict1["bidder"] = list[2]
                    # 时间
                    dict1["time"] = list[4]
                    bidding_record.append(dict1)
                item["bidding_record"] = bidding_record
            except:
                item["bidding_record"] = []
        # 优先购买权人
        item["preemptor"] = []
        # 图片
        item["images"] = response.xpath('//*[@id="bdjs11"]/img/@src').extract()
        # 变卖预缴款
        item["sale_advance_payment"] = ""
        # 竞拍方式类型
        item["auction_type"] = re.search("拍卖|变卖", item["auction_phase"]).group()
        # 保证金须知
        item["margin_notes"] = []
        # 保留价
        item["reserve_price"] = ""
        # 标的物所在地
        if item["type"] == "房产":
            item["location"] = item["name"]
        else:
            item["location"] = ""
        rul = response.xpath('//*[@id="bdjs11"]/table[2]').get()
        # bdjs_list = [i.replace("\xa0", "").replace("\n", "").replace(" ", "") for i in bdjs_list if i.strip() != ""]
        result_dict, result_list = extract_table_new(rul)
        item_dict = get_table_info(result_dict, result_list)

        item.update(item_dict)
        # 视频url地址
        item["videos"] = ""
        # 公告日期
        try:
            item["publish_date"] = re.search("<p>(.{1,4}年.{1,3}月.{1,3}日)</p>", item["announcement"][0]).group(1)
        except:
            item["publish_date"] = ""

        # print(pqjs)
        # print(response.url)
        # yield item
        print(item)
