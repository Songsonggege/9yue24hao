# author:胡已源
# datetime:2019/8/30 上午11:13
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
from common_utils import user_agnet_utils
from typing import Tuple, Optional, List, Union
from aiosocksy.connector import ProxyConnector, ProxyClientRequest
from aiohttp import ClientSession, ClientResponse, FormData
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

"""定义队列属性"""


class QueueConfig(object):

    def __init__(self):
        self.task_queue = Queue()  # 任务队列
        self.full_data_task_queue = LifoQueue()  # 已经完成下载的队列
        self.result_queue = Queue()  # 数据队列

    def __str__(self):
        s = "当前task_queue任务队列存数量:%s,已完成数据队列数量:%s" % (self.task_queue.qsize(), self.full_data_task_queue.qsize())
        return s


class Task(object):
    """
    用于封装初始化任务
    """

    def __init__(self, url: str, method='GET', headers: dict = None, json_form: dict = None,
                 data: dict = None, cookies: dict = None, meta: dict = None, encoding='utf-8', callback=None):
        self.url: str = url
        self.method: str = str(method).upper()
        self.headers: dict = headers
        self.cookies: dict = cookies or {}
        self.data: dict = data
        self.json: dict = json_form
        self.encoding = encoding
        self.status_code: int = 0
        self.response_headers: dict = {}
        self.html: str = ""
        self.meta = dict(meta) if meta else None
        self.callback = callback

    def __str__(self):
        return "<%s %s>" % (self.method, self.url)

    __repr__ = __str__

    def copy(self):
        """Return a copy of this Task"""
        return self.replace()

    def replace(self, *args, **kwargs):
        """Create a new Task with the same attributes except for those
        given new values.
        """
        for x in ['url', 'method', 'headers', 'cookies', 'data', 'encoding', 'meta', 'callback']:
            kwargs.setdefault(x, getattr(self, x))
        cls = kwargs.pop('cls', self.__class__)
        return cls(*args, **kwargs)


if __name__ == '__main__':
    headers = user_agnet_utils.getheaders()
    url = "http://credit.jian.gov.cn/JaxyMh/xygs/getSgsList.jsons"
    data = {
        "curpage": 1,
        "percount": "15",
        "type": "xzcf",
        "zonecode": "360800"
    }
    task = Task(url, method="post", headers=headers, data=data, meta={"curpage": 1})

    new_task = task.copy()
    print(new_task.__str__())
    print(new_task.headers)
    print(new_task.data)
