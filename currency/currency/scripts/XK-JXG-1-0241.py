# author:胡已源
# datetime:2019/8/26 上午9:36
# software: PyCharm


import re
import ssl
import six
import json
import time
import random
import asyncio
import aiohttp
import traceback
import pymongo
import requests
from lxml import etree
from asyncio.queues import Queue, LifoQueue
from asyncio import QueueEmpty
from requests import Session
from common_utils import user_agnet_utils, common
from typing import Tuple, Optional, List, Union
from aiosocksy.connector import ProxyConnector, ProxyClientRequest
from aiohttp import ClientSession, ClientResponse, FormData
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from currency.currency.scripts.core import aio

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait


class Common(object):
    cookies_list = []  # Cookie列表
    task_queue = Queue()  # 任务队列
    full_data_task_queue = LifoQueue()  # 已经完成下载的队列
    result_queue = Queue()  # 数据队列
    session: Session() = requests.session()
    session.keep_alive = False


class Task(object):
    """
    用于封装初始化任务
    """

    def __init__(self, url: str, method='GET', headers: dict = None, json_form: dict = None,
                 data: dict = None, cookies: dict = None, meta: dict = None, encoding='utf-8', callback=None):
        self.method: str = str(method).upper()
        self.encoding = encoding
        self.url: str = url
        self.json: dict = json_form
        self.data: dict = data
        self.html: str = ""
        self.response_headers: dict = {}
        self.status_code: int = 0
        self.cookies: dict = cookies or {}
        self.headers: dict = headers
        self.meta = dict(meta) if meta else None
        self.callback = callback

    def __str__(self):
        return "<%s %s>" % (self.method, self.url)

    __repr__ = __str__

    def copy(self):
        """Return a copy of this Request"""
        return self.replace()

    def replace(self, *args, **kwargs):
        """Create a new Request with the same attributes except for those
        given new values.
        """
        for x in ['url', 'method', 'headers', 'body', 'cookies', 'meta']:
            kwargs.setdefault(x, getattr(self, x))
        cls = kwargs.pop('cls', self.__class__)
        return cls(*args, **kwargs)


async def get_cookies():
    """
    通过无头浏览器生成动态Cookie
    :return: 以字典形式返回Cookie
    """
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--proxy-server={}'.format(await get_proxy(Common.session)))
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--hide-scrollbars')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    timeout = 10
    print("进入selenium,开始生成Cookie")
    driver.get("http://credit.jian.gov.cn/JaxyMh/xygs/gotoXysgs.do")
    # 等待页面
    WebDriverWait(driver, timeout).until(
        lambda d: d.find_element_by_xpath("//div[@class='header-nav']//div[@class='content']")
    )
    # 有时候需要加载两次
    driver.get("http://credit.jian.gov.cn/JaxyMh/xygs/gotoXysgs.do")
    timeout = 10
    # 等待页面
    WebDriverWait(driver, timeout).until(
        lambda d: d.find_element_by_xpath("//div[@class='js-xzxk-grid listtableDiv']")
    )
    # 这里我们使用cookie对象进行处理
    cookies = driver.get_cookies()
    cookies_dict = dict()
    for cookie in cookies:
        cookies_dict[cookie['name']] = cookie['value']
    print("生成后的Cookie:{}".format(cookies_dict))
    driver.quit()
    return cookies_dict


async def check_cookies():
    while True:
        await asyncio.sleep(60)
        for index, item in enumerate(Common.cookies_list):
            print("开始检测Cookie")
            data_entity = {
                "id": "05509bc846cb460798540736140db163",
                "type": "xzcf",
            }
            headers = user_agnet_utils.getheaders()
            # headers['Connection'] = 'close'
            entity_response = Common.session.post(
                "http://credit.jian.gov.cn/JaxyMh/xygs/getXygsDetail.json",
                data=data_entity,
                headers=headers,
                cookies=item,
                # proxies={"http": get_proxy(Common.session)}
            )

            data_list = {
                "curpage": str(index),
                "percount": "15",
                "type": "xzcf",
                "zonecode": "360800"
            }
            list_response = Common.session.post(
                "http://credit.jian.gov.cn/JaxyMh/xygs/getSgsList.jsons",
                data=data_list,
                headers=headers,
                cookies=item,
                # proxies={"http": get_proxy(Common.session)}
            )
            list_is_ok: bool = len(list_response.text) > 0
            entity_is_ok: bool = len(entity_response.text) > 0
            print("列表Cookie是否有效：", list_is_ok)
            print("实体Cookie是否有效：", entity_is_ok)
            if not (list_is_ok and entity_is_ok):
                del Common.cookies_list[index]
                # 重新添加Cookie
                Common.cookies_list.append(await get_cookies())


def get_proxy(session: Session()):
    """
    获取IP
    :return:代理ip
    """
    # session = requests.session()
    for i in range(10):
        ip = session.get("http://172.19.89.17:5010/get/")
        proxy = "http://" + ip.text
        try:
            response = requests.get('http://icanhazip.com/', proxies={'http': ip.text}, timeout=1)
            proxyIP = response.text.strip()
            thisIP = ip.text[0:ip.text.rfind(":")].strip()
            if proxyIP == thisIP:
                print("代理IP:'" + proxyIP + "'有效！")
                return proxy
            else:
                print("代理IP无效！")
        except:
            # await asyncio.sleep(0.1)
            print("获取代理超时")


async def parse_detail(task: Task):
    if task.status_code == 200 and len(task.html) > 0:

        json_object: dict = json.loads(task.html)

        task.url = task.meta["url"]
        name = ""
        date = ""
        publisher = "江西省吉安市人民政府"
        regionCode = "360800"
        type = ""

        data: dict = json_object['data']
        string_builder: str = ""  # 拼接的正文
        # 数据存放
        dataList: List[dict] = []
        paragraphList: List[str] = []

        if data.get("cf_wsh"):
            string_builder += "<p>行政处罚决定书文号：{}</p>".format(data.get("cf_wsh"))

        if data.get("cf_ajmc"):
            string_builder += "<p>处罚名称：{}</p>".format(data.get("cf_ajmc"))
            name = data.get("cf_ajmc")

        if data.get("cf_cflb"):
            string_builder += "<p>处罚类别：{}</p>".format(data.get("cf_cflb"))

        if data.get("cf_sy"):
            string_builder += "<p>处罚事由：{}</p>".format(data.get("cf_sy"))

        if data.get("cf_yj"):
            string_builder += "<p>处罚依据：{}</p>".format(data.get("cf_yj"))

        if data.get("cf_xdr_mc"):
            string_builder += "<p>行政相对人名称：{}</p>".format(data.get("cf_xdr_mc"))
            if not name:
                name = data.get("cf_xdr_mc") + data.get("cf_sy", "")

        if data.get("cf_xdr_shxym"):
            string_builder += "<p>行政相对人代码_1 (统一社会信用代码)：{}</p>".format(data.get("cf_xdr_shxym"))

        if data.get("cf_xdr_zdm"):
            string_builder += "<p>行政相对人代码_2 (组织机构代码)：{}</p>".format(data.get("cf_xdr_zdm"))

        if data.get("cf_xdr_gsdj"):
            string_builder += "<p>行政相对人代码_3 (工商登记码)：{}</p>".format(data.get("cf_xdr_gsdj"))

        if data.get("cf_xdr_swdj"):
            string_builder += "<p>行政相对人代码_4 (税务登记号)：{}</p>".format(data.get("cf_xdr_swdj"))

        if data.get("cf_xdr_sfz"):
            string_builder += "<p>行政相对人代码_5 (居民身份证号)：{}</p>".format(data.get("cf_xdr_sfz"))

        if data.get("cf_fr"):
            string_builder += "<p>法定代表人姓名：{}</p>".format(data.get("cf_fr"))

        if data.get("cf_jg"):
            string_builder += "<p>处罚结果：{}</p>".format(data.get("cf_jg"))

        if data.get("cf_sxq"):
            string_builder += "<p>处罚生效日期：{}</p>".format(data.get("cf_sxq"))

        if data.get("cf_jzq"):
            string_builder += "<p>处罚截止日期：{}</p>".format(data.get("cf_jzq"))

        if data.get("cf_xzjg"):
            string_builder += "<p>处罚机关：{}</p>".format(data.get("cf_xzjg"))

        if data.get("cf_zt"):
            string_builder += "<p>当前状态：{}</p>".format(data.get("cf_zt"))

        if data.get("dfbm"):
            string_builder += "<p>地方编码：{}</p>".format(data.get("dfbm"))

        if data.get("sjc"):
            string_builder += "<p>数据更新时间戳：{}</p>".format(data.get("sjc"))
            date = data.get("sjc")

        if data.get("bz"):
            string_builder += "<p>备注：{}</p>".format(data.get("bz"))

        paragraphList.append(string_builder)

        # 匹配文号正则
        identity_condition = r"<p>行政处罚决定书文号[^无<>]+?(?=</p>)"

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

        # 数据封装
        for para in paragraphList:
            para = re.sub(r"<p>序号.*?</p>", "", para)
            para = re.sub(r"：", ":", para)
            para = re.sub(r"\ue2d1", "", para)
            result_object = {
                "name": name,
                "createdAt": date,
                "publisher": publisher,
                "type": type,
                "regionCode": regionCode,
                "paragraph": [para],
                "source_url": task.url
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

            # 封装处罚日期
            prTarget = common.reg_matching_text(prTarget_condition, para).strip()
            if common.is_not_empty(prTarget):
                result_object["prTarget"] = [prTarget]

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

            if common.is_not_empty(result_object["paragraph"][0]):
                dataList.append(result_object)

            for data_dict in dataList:
                if data_dict.get("identifier") and len(re.compile(".*").findall(
                        data_dict.get("identifier"))) > 0:

                    data_dict['adid'] = common.md5Hex(data_dict.get("regionCode") + "-" + re.sub("[^a-zA-Z0-9\u4e00-\u9fa5]", "",
                                                                                                 data_dict.get("identifier")))
                    data_dict['idMethod'] = "1"
                    continue
                elif len(dataList) == 1:
                    data_dict['adid'] = common.md5Hex(task.url)
                    data_dict['idMethod'] = "2"
                else:
                    paragraph = data_dict.get("paragraph")
                    paragraph = re.sub("\s|\r|\t|\n|[^a-zA-Z0-9\u4e00-\u9fa5]", "", paragraph)
                    data_dict['adid'] = common.md5Hex(paragraph)
                    data_dict['idMethod'] = "3"

            for data in dataList:
                print("当前抓取的实体页来自：", task.meta['curpage'] + "页")
                print("数据解析结果：", data)
                Common.result_queue.put_nowait(data)


async def parse_list(task: Task):
    if task.status_code == 200:
        json_object: dict = json.loads(task.html)
        for item in json_object['data']['retlist']:
            id = item['id']
            name = item['cf_xdr_mc']
            url = "http://credit.jian.gov.cn/JaxyMh/xygs/getXygsDetail.json"
            data = {
                "id": id,
                "type": "xzcf"
            }
            print("当前抓取第%s" % task.data['curpage'] + "页面,抓取的行政主体:", name)
            await Common.task_queue.put(
                Task(url=url,
                     data=data,
                     method="post",
                     callback=parse_detail,
                     meta={"curpage": task.data['curpage'],
                           "url": "http://credit.jian.gov.cn/JaxyMh/xygs/gotoXzcfDetail.do?id={}&type=xzcf".format(id)}
                     )
            )


async def start_requests():
    headers = user_agnet_utils.getheaders()
    for index in range(1, 82013):
        url = "http://credit.jian.gov.cn/JaxyMh/xygs/getSgsList.jsons"
        data = {
            "curpage": str(index),
            "percount": "15",
            "type": "xzcf",
            "zonecode": "360800"
        }
        await Common.task_queue.put(Task(url, method="post", headers=headers, data=data, callback=parse_list, meta={"curpage": str(index)}))


async def speed_monitor():
    while Common.task_queue.qsize() != 0:
        old_queue_len = Common.task_queue.qsize()
        await asyncio.sleep(5)
        new_queue_count = Common.task_queue.qsize()
        print('=================')
        print('speed = ', (old_queue_len - new_queue_count) / 5)


async def monitor_finish():
    """
    每隔1秒钟查看asyncio中的任务队列已经完成
    :return: 抛出异常程序结束
    """
    while len(asyncio.Task.all_tasks()) > 3:
        await asyncio.sleep(1)
    await asyncio.sleep(10)
    raise SystemExit()


async def download(task: Task, session: ClientSession()):
    # 获取必请求参数
    headers = user_agnet_utils.getheaders()
    cookie = random.choice(Common.cookies_list)
    proxy = get_proxy(Common.session)
    for _ in range(3):
        print("第%s次请求" % _)
        if "POST" == task.method.upper():
            html, status_code, response_headers = await aio.fetch_post(session, task.url, data=task.data, headers=headers, cookies=cookie, proxy=proxy)
            task.html = html
            task.status_code = status_code
            task.response_headers = response_headers
            if len(html) > 0:
                Common.full_data_task_queue.put_nowait(task)
                break


async def core():
    sem = asyncio.Semaphore(30)  # 信号量，控制协程数，防止爬的过快
    connector = ProxyConnector()
    async with aiohttp.ClientSession(
            connector=connector,
            request_class=ProxyClientRequest
    ) as session:
        while True:
            with(await sem):
                try:
                    task: Task = Common.task_queue.get_nowait()
                except QueueEmpty as Q:
                    print("task_queue队列为空", Q)
                    return
                try:
                    # await asyncio.sleep(1)
                    await download(task, session)
                    # await task.callback(task)
                except Exception as e:
                    print("下载错误:", task.meta['curpage'] + "页", e)
                    print(traceback.format_exc())
                    await asyncio.sleep(0.2)
                    continue


async def data_parsing():
    while True:
        try:
            task: Task = Common.full_data_task_queue.get_nowait()
            await task.callback(task)

        except QueueEmpty as Q:
            # print("解析数据异常：", Q)
            # print(traceback.format_exc())
            await asyncio.sleep(0.2)
            continue


async def push_results():
    host = '127.0.0.1'
    port = 27017
    database = 'beehive'
    collection_name = 'XK-JXG-1-0241_CF'
    connection: AsyncIOMotorClient() = AsyncIOMotorClient(
        host,
        port
    )
    db = connection[database]
    collection = db[collection_name]

    temp_q = []
    while True:
        try:
            await asyncio.sleep(3)
            for _ in range(Common.result_queue.qsize()):
                temp_q.append(await Common.result_queue.get())
            if len(temp_q) > 0:
                await save_data(temp_q, collection)
                temp_q.clear()
        except:
            print(traceback.format_exc())


async def save_data(data, collection):
    print("进入数据添加,当前添加条数：", len(data))
    await collection.insert_many(data)


async def main():
    # 生成动态Cookie
    for i in range(5):
        Common.cookies_list.append(await get_cookies())
    # 添加初始化任务
    await start_requests()
    for index in range(10):
        loop.create_task(core())
    # for index in range(3):
    loop.create_task(data_parsing())
    loop.create_task(push_results())
    loop.create_task(check_cookies())
    loop.create_task(monitor_finish())
    loop.create_task(speed_monitor())


if __name__ == '__main__':
    # 获取事件循环
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()
