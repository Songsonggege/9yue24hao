# -*- coding: utf-8 -*-
import re
import scrapy
import urllib.parse

from ..utils import common
from ..items import CfItem
from typing import List
from bs4 import BeautifulSoup

"""中国银监会"""


class ChinaBankingRegulatoryCommissionSpider(scrapy.Spider):
    name = 'china_banking'
    allowed_domains = ['http://www.cbrc.gov.cn']
    start_urls = ['http://http://www.cbrc.gov.cn/zhuanti/xzcf/get2and3LevelXZCFDocListDividePage//1.html?current=1/']

    headers = {
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
    }

    def start_requests(self):

        url = 'http://www.cbrc.gov.cn/zhuanti/xzcf/get2and3LevelXZCFDocListDividePage//1.html?current={}'
        for i in range(1):
            yield scrapy.Request(url=url.format(i), callback=self.parse, headers=self.headers)

    def parse(self, response):

        for tr in response.xpath("//table[@id='testUI']//tr"):
            # 定义数据
            items = CfItem()
            items['name'] = tr.xpath("./td[1]/a/@title").get()
            items['createdAt'] = tr.xpath("./td[2]/text()").get()
            url = tr.xpath("./td[1]/a/@href").get()
            url = urllib.parse.urljoin(response.url, url)
            print(items['name'])
            print(items['createdAt'])
            print(url)
            yield scrapy.Request(url=url, meta={'list_items': items}, callback=self.parse_detail, headers=self.headers, dont_filter=True)

    def parse_detail(self, response):
        name = ""
        date = ""
        publisher = "天津市中国银行业监督管理委员会监管局"
        regionCode = "210800"
        type = "environmental"
        key_word = "云津沪甬渝粤"
        items = response.meta['list_items']

        # 数据存放
        dataList: List[dict] = []
        paragraphList: List[str] = []

        # xpath设置
        name_css = ""
        date_xpath = ""
        paragraph_css = "div[class*=Section]"

        # 匹配文号正则
        identity_condition = r"[【(（〔﹝]?[" + key_word + "].{1,10}([【〔﹝(\[\s])?([12][\d]{3}|[\d]+)([\s\])﹞〕】])?[\s]?([\S]{1,7})[\s]?号"

        # 设置正则匹配正文中的行政主体
        prPrincipal_condition = r"<p>([^:<>]{0,10}(经营者名称|相对人名称|社团名称|被处罚单位名称|企业名称|被处罚[^:<>]{0,5}名称|当事人)[^:<>]{0,10}[：:])[^<>]{2,50}?(。|</p>)|=<p>(姓名|名称)[：:][^无<>]{2,50}?</p>|(当.{0,2}事.{0,2}人.{0,4}|被.{0,3}罚.{0,3}(单位|人).{0,5}(姓名|名称)?|[企单].{0,2}[位业].{0,2}名.{0,2}称)[:：]\\s?[^无<>]*?([\\s，性地。；]|</p>|经营地址|住址)"

        # 设置正则匹配正文中的法人代表
        PrLegalPerson_condition = r"<p>([^:<>执]{0,5}法[^:<>]{0,5}人[^:证号码<>]{0,10})[：:][^无<>]{1,10}?(?=</p>|。|职务)|(法.{0,8}人|经.{0,3}营.{0,3}[者人].{0,3}(姓名)?|负.{0,3}责.{0,3}人|院.{0,3}长).{0,2}[:：][^无<>]*?([\\s职；。、）]|</p>)"

        # 设置正则匹配正文中的信用代码
        prCreditCode_condition = r"<p>([^:<>]{0,15}(信用代码|机构代码|相对人代码)[^:<>]{0,15})[：:][^无<>]{4,30}?(</p>)|(证.{0,5}号.{0,3}码.{0,3}|信.{0,3}用.{0,3}代.{0,3}码|注.{0,3}册.{0,3}号|营.{0,3}业.{0,3}执.{0,3}照|组.{0,3}织.{0,3}机.{0,3}构.{0,3}代.{0,3}码|身.{0,5}号码.{0,3})(.{0,5})?[:：]\\s?.*?(地址|</p>|[\\s，,\\(、详；\\)])"

        # 设置正则匹配正文中的处罚事由
        prCause_condition = r"<p>([^:<>]{0,10}(事由|违法事实)[^:<>]{0,10}[：:])[^<>]{3,200}?</p>"

        # 设置正则匹配正文中的处罚依据
        prGist_condition = r"<p>([^:<>]{0,10}依据[^:<>]{0,10})[：:][^<>]{3,200}?</p>"

        # 设置正则匹配正文中的处罚时间
        prPunishmentAt_condition = r"<p>([^:<>]{0,5}(罚.{0,8}(时间|日期)|决定日期)[^:<>]{0,5})[：:][^无<>]{1,30}?</p>|<p>\\d{4}.\\d{1,2}.\\d{1,2}.</p>"

        # 设置正则匹配正文中的处罚结果
        prTarget_condition = r"<p>[^:<>]{0,5}(罚[^:<>]{0,5}(款|额)|处罚.?结果|处罚内容)[^:<>]{0,5}[：:][^无<>]{1,100}?</p>|<p>行政处罚决定[：:][^无<>]{1,100}?</p>"

        # 设置正则匹配正文中的处罚类别
        categories_condition = r"<p>([^:<>]{0,5}(类别1|处罚类型)[^:<>]{0,5})[：:][^无<>]{1,30}?</p>"

        # 设置正则匹配正文中的电话
        prPhone_condition = r"<p>([^:<>]{0,5}(电话)[^:<>]{0,5})[：:][^无<>]{1,30}?</p>|电话[:：][^无<>]*?[\\s。\\)），,\\u4e00-\\u9fa5]"

        # 设置正则匹配正文中的地址
        prAddress_condition = r"<p>([^:<>]{0,5}(地址)[^:<>]{0,5})[：:][^无<>]{1,100}?(邮|</p>)|(住[址所]|营业场所|经营地址|经营场所|地.{0,12}址)[:：][^无<>]*?([；,、）\\)，邮]|</p>|厂长|本机关|法.{0,8}人)"

        # 表头正则
        header_condition = r"(被处罚当事人姓名或名称|主要违法事实|违法当事人|作出处罚决定的机关|案由|决定书编号|处罚时间|处罚结果|被处罚单位|违法违规事实|行政处罚决定书文号|案件名称|违法事实|处罚类别|处罚依据|行政相对人名称|法定代表人姓名|处罚决定的日期)"

        # 文本
        document_text = response.text

        # 获取文档对象
        document = BeautifulSoup(document_text, features="lxml")

        if items.get("name"):
            name = items.get("name")
        elif name_css:
            name = document.select_one(name_css).get_text(strip=True).replace("\xa0", "").replace("\u3000", "")

        if items.get("createdAt"):
            date = common.extract_date(items["createdAt"])
        elif date_xpath:
            date = common.extract_date(response.xpath(date_xpath).get())

        # 正文
        paragraph = response.css(paragraph_css).get()
        paragraph = common.filter_tags(paragraph, response.url, flag=True)

        document = document.select_one(paragraph_css)
        if document is None:
            raise RuntimeError("document为空")

        # 解析表格
        for table_element in document.select("table"):
            actual_index: int = 0  # 表头行
            table_vertical: int = 0  # 记录表头匹配次数
            back_table: int = 0
            string_builder: str = ""  # 拼接的正文
            table_heads: List[str] = []  # 表头列表

            # 遍历tr和td
            tr_elements = table_element.select("tr,thead")
            # 过滤有空表格的情况
            if len(tr_elements) < 2:
                continue
            for index, tr_element in enumerate(tr_elements):
                td_elements = tr_element.select("td,th")
                if re.compile(header_condition).findall(tr_element.get_text(strip=True)).__len__() >= 3:
                    print("进入横表匹配！！")
                    actual_index = index
                    colspan = 0
                    for head_td in td_elements:
                        if head_td.has_attr("colspan"):
                            colspan += int(head_td['colspan'])
                            for i in range(colspan):
                                table_heads.append(tr_elements[actual_index + 1].select("td").get_text(strip=True))
                        else:
                            table_heads.append(head_td.get_text(strip=True))
                    print("表头列表：", table_heads)
                    break
                else:
                    for td in td_elements:
                        td_value: str = td.get_text(strip=True)
                        if not td_value:
                            continue
                        # 如果一行中匹配到了表头值大于
                        if re.compile(header_condition).search(td_value):
                            if td.has_attr("rowspan"):
                                back_table += 1
                            table_vertical += 1
                            break

                # 只循环10行
                if len(tr_elements) > 10 and index == 10:
                    break
            print("匹配竖向表格次数：", table_vertical)
            if table_vertical > 3:
                for tr_em in tr_elements:
                    td_ems = tr_em.select("td,th")

                    if len(td_ems) < 2:
                        continue
                    tdTitle: str = ""
                    tdValue: str = ""
                    if back_table > 0:
                        title = td_ems[len(td_ems) - 2].get_text(strip=True).replace("：", ":")
                        value = td_ems[len(td_ems) - 1].get_text(strip=True).replace("：", ":")
                        string_builder += "<p>{}:{}</p>".format(title, value)
                    else:
                        for num in range(len(td_ems)):
                            # 偶数作为表头
                            tdTitle: str = ""
                            if num % 2 == 0:
                                tdTitle = td_ems[num].get_text(strip=True).replace("：", ":")
                                if not common.is_not_empty(tdTitle):
                                    continue

                            if num + 1 >= len(td_ems):
                                continue

                            tdValue = td_ems[num + 1].get_text(strip=True)
                            # 拼接正文
                        string_builder += "<p>{}:{}</p>".format(tdTitle, tdValue)
                # 添加至文本集合
                paragraphList.append(string_builder)
            else:
                if not table_heads:
                    continue
                print("---进入横表解析---")
                for run_index in range(actual_index + 1, len(tr_elements)):
                    string_builder = ""
                    if run_index >= len(tr_elements):
                        continue
                    for index, tds in enumerate(tr_elements[run_index].select("td,th")):
                        title = table_heads[index]
                        value = tds.get_text(strip=True)

                        string_builder += "<p>{}:{}</p>".format(title, value)
                    if len(string_builder) > 0:
                        paragraphList.append(string_builder)

        flag = True
        # 存附件
        url_set = set()
        for a_element in document.select("a[href]"):
            if a_element is not None:
                url: str = a_element["href"]
                if common.is_not_empty(url) and not url.find("许可") > 1:
                    flag = False
                    url = urllib.parse.urljoin(response.url, url)
                    url_set.add(url)
        # 存图片
        image_any = []
        for img_element in document.select("img[src]"):
            if img_element is not None:
                url: str = img_element["src"]
                if re.search("(gif|icons|file://)", url):
                    continue
                url = urllib.parse.urljoin(response.url, url)
                image_any.append(url)

        if len(paragraphList) == 0 and flag:
            paragraphList.append(paragraph)

        # 数据封装
        for para in paragraphList:
            para = re.sub(r"<p>序号.*?</p>", "", para)
            para = re.sub(r"：", ":", para)
            result_object = {
                "name": name,
                "createdAt": date,
                "publisher": publisher,
                "type": type,
                "regionCode": regionCode,
                "paragraph": [para],
                "source_url": response.url
            }

            # 封装文号
            identifier = common.reg_matching_text(identity_condition, name).strip()
            if common.is_not_empty(identifier):
                result_object["identifier"] = identifier
            else:
                if common.reg_matching_text(identity_condition, para).strip():
                    result_object["identifier"] = common.reg_matching_text(identity_condition, para).strip()
            # 封装相对人名称
            prPrincipal = common.reg_matching_text(prPrincipal_condition, para).strip()
            if common.is_not_empty(prPrincipal):
                result_object["prPrincipal"] = prPrincipal
            else:
                prPrincipal_matcher = re.compile("[^\x00-\xff]+(公司|厂|店)[:：]").search(paragraph)
                if prPrincipal_matcher:
                    result_object["prPrincipal"] = prPrincipal_matcher.group().replace("：", "").replace(":", "")

            # 封装处罚事由
            prCause = common.reg_matching_text(prCause_condition, para).strip()
            if common.is_not_empty(prCause):
                result_object["prCause"] = prCause

            # 封装处罚依据
            prGist = common.reg_matching_text(prGist_condition, para).strip()
            if common.is_not_empty(prGist):
                result_object["prGist"] = prGist

            # 封装信用代码
            prCreditCode = common.reg_matching_text(prCreditCode_condition, para).strip()
            if common.is_not_empty(prCreditCode):
                result_object["prCreditCode"] = prCreditCode

            # 封装法人
            prLegalPerson = common.reg_matching_text(PrLegalPerson_condition, para).strip()
            if common.is_not_empty(prLegalPerson):
                result_object["prLegalPerson"] = prLegalPerson

            # 封装处罚日期
            prPunishmentAt = common.reg_matching_text(prPunishmentAt_condition, para).strip()
            if common.is_not_empty(prPunishmentAt):
                result_object["prPunishmentAt"] = prPunishmentAt
            else:
                # 取最后一个p标签的内容
                new_text = paragraph[paragraph.rfind("<p>"):paragraph.rfind("</p>")]
                prPunishmentAt = common.chinese_date_parser(new_text)
                if common.is_not_empty(prPunishmentAt):
                    result_object["prPunishmentAt"] = prPunishmentAt

            # 封装处罚日期
            prTarget = common.reg_matching_text(prTarget_condition, para).strip()
            if common.is_not_empty(prTarget):
                result_object["prTarget"] = prTarget

            # 封装处罚类别
            categories = common.reg_matching_text(categories_condition, para).strip()
            if common.is_not_empty(categories):
                result_object["categories"] = categories

            # 封装电话
            prPhone = common.reg_matching_text(prPhone_condition, para).strip()
            if common.is_not_empty(prPhone):
                result_object["prPhone"] = prPhone

            # 封装地址
            prAddress = common.reg_matching_text(prAddress_condition, para).strip()
            if common.is_not_empty(prAddress):
                result_object["prAddress"] = prAddress

            if image_any.__len__() > 0:
                result_object["images"] = image_any

            if common.is_not_empty(result_object["paragraph"][0]):
                dataList.append(result_object)

        for url_str in url_set:
            result_object = {
                "name": name,
                "createdAt": date,
                "publisher": publisher,
                "type": type,
                "regionCode": regionCode,
                "paragraph": ["<a href ='" + url_str + "'" + ">" + "</a>"],
                "url": url_str,
                "source_url": response.url
            }

            if common.is_not_empty(result_object["paragraph"][0]):
                dataList.append(result_object)

        map_condition = {
            "hashId": "adid",
            "contentKey": "paragraph",
            "caseKey": "identifier",
            "urlIsAvailable": "url",
            "idMatcher": identity_condition
        }
        # hash数据
        common.hash_value(dataList, map_condition, response.url)

        for data in dataList:
            yield data
