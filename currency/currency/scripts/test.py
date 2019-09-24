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

from currency.currency.scripts.config.config import Task
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


async def get_cookies():
    """
    通过无头浏览器生成动态Cookie
    :return: 以字典形式返回Cookie
    """
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--proxy-server={}'.format(await get_proxy(Common.session)))
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--hide-scrollbars')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    # chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    print("进入selenium,开始生成Cookie")
    driver.get("https://www.creditchina.gov.cn/api/EPAndPS/getPsListByType?keyword=&dataType=1&page=5&pageSize=10")
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
        await asyncio.sleep(15)
        for index, item in enumerate(Common.cookies_list):
            print("开始检测Cookie")
            headers = user_agnet_utils.getheaders()
            entity_response = Common.session.get(
                "https://www.creditchina.gov.cn/api/EPAndPS/getPsListByType?keyword=&dataType=1&page=5&pageSize=10",
                headers=headers,
                cookies=item,
                proxies={"http": get_proxy(Common.session)}
            )
            entity_is_ok: bool = "results" in entity_response.text
            print("实体Cookie是否有效：", entity_is_ok)
            if not entity_is_ok:
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
   pass


async def parse_list(task: Task):
    if task.status_code == 200:
        pass

async def start_requests():
    headers = user_agnet_utils.getheaders()
    for index in range(1, 10):
        url = "https://www.creditchina.gov.cn/api/EPAndPS/getPsListByType?keyword=&dataType=1&page={}&pageSize=10"
        await Common.task_queue.put(
            Task(url, method="get", headers=headers, callback=parse_list, meta={"curpage": str(index)})
        )


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
    # loop.create_task(push_results())
    loop.create_task(check_cookies())
    loop.create_task(monitor_finish())
    loop.create_task(speed_monitor())


if __name__ == '__main__':
    # 获取事件循环
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()
