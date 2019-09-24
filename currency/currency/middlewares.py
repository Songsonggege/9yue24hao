# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import re
import logging
import execjs
import time
import requests
from requests import Session
from scrapy import Spider, Request

from .utils import common
from fake_useragent import UserAgent
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

# 日志对象
logger = logging.getLogger(__name__)


class SeleniumMiddleware(object):
    """集成Selenium中间件"""

    def __init__(self, timeout=10, service_args=None, path=''):
        # 是否启用selenium中间件根据request对象中是否有设置参数
        self.service_args = service_args
        self.timeout = timeout
        self.chrome_options = webdriver.ChromeOptions()
        for arg in self.service_args:
            self.chrome_options.add_argument(arg)
        # 添加后可以避免被服务器检测
        self.chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        # 初始化driver对象
        self.driver = webdriver.Chrome(chrome_options=self.chrome_options, executable_path=path)

    def __del__(self):
        self.driver.close()

    def process_request(self, request: Request, spider: Spider):
        """
        用HeadlessChrome抓取页面
        :param request: Request对象
        :param spider: Spider对象
        :return: HtmlResponse响应
        """
        logger.info('HeadlessChrome 开始执行')
        try:
            if spider.name == "china_banking_regulatory_commission":
                self.driver.get(request.url)
                if request.url.find("current") > 0:
                    WebDriverWait(self.driver, self.timeout).until(
                        lambda d: d.find_elements_by_xpath("//table[@id='testUI']//tr")
                    )
                if request.url.find("docView") > 0:
                    WebDriverWait(self.driver, self.timeout).until(
                        lambda d: d.find_elements_by_xpath("//div[contains(@class,'Section1')]")
                    )
                return HtmlResponse(url=request.url, body=self.driver.page_source, request=request, encoding='utf-8', status=200)

            if spider.name == "fly":
                self.driver.get(request.url)
                if request.url.find("index") > 0:
                    WebDriverWait(self.driver, self.timeout).until(
                        lambda d: d.find_elements_by_xpath("//td[@class='2016_erji_content']")
                    )
                return HtmlResponse(url=request.url, body=self.driver.page_source, request=request, encoding='utf-8', status=200)

            if spider.name == "fly2":
                self.driver.get(request.url)
                if request.url.find("index") <= 0:
                    WebDriverWait(self.driver, self.timeout).until(
                        lambda d: d.find_elements_by_xpath("//ul[@id='search-result-list']/li[@class='tab1-item']")
                    )
                # self.driver.find_element_by_xpath("//a[@class='page-link next']").click()
                return HtmlResponse(url=request.url, body=self.driver.page_source, request=request, encoding='utf-8', status=200)

        except TimeoutException as err:
            logger.info(f"chrome getting page error,Exception = {err}")
            return HtmlResponse(url=request.url, status=500, request=request)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(timeout=crawler.settings.get('SELENIUM_TIMEOUT'),
                   service_args=crawler.settings.get('CHROME_SERVICE_ARGS'),
                   path=crawler.settings.get('EXECUTABLE_PATH'))


class ChinaBankingCookiesMiddleware(object):
    def __init__(self, crawler):
        self.is_turn_on = crawler.settings.get('COOKIE_IS_TURN_ON')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        if spider.name == self.is_turn_on:
            print("请求之前的cookies：", str(request.cookies))
            session = requests.Session()
            headers = {
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
            }
            url = "http://www.cbrc.gov.cn/chinese/home/docView/0BC078E930274E56B298FD73C0E407FC.html"
            response = session.get(url, headers=headers)
            route_script = re.findall('<script>(.*?)</script>', response.text, re.S)[0]
            route_script = route_script.replace('eval(y.replace', 'return (y.replace')
            resHtml = 'function getClearance(){' + route_script + '}'
            # 执行获取新的cookies加密Js
            script_result = execjs.compile(resHtml).call('getClearance')

            var_name = re.findall('var(.*?)=function', script_result).pop()
            # 替换不要的Js参数
            script_result = re.sub('document.createElement.*?firstChild.href', "\'" + url + "\'", script_result)
            script_result = script_result.replace('document.cookie', 'cookie')
            script_result = script_result[:script_result.find('if((function()')]

            cookie_script = "function getClearanceV2(){  var cookie = '', window = new Object(); " + script_result + var_name + '();' + '  return cookie;}'
            cookie_script = re.sub('setTimeout.*?1500\);', '', cookie_script)

            # 执行Js获取最终参数
            cookies = execjs.compile(cookie_script).call('getClearanceV2')
            __jsl_clearance = re.findall('__jsl_clearance=(.*?);Expires', cookies, re.S).pop()
            session.cookies['__jsl_clearance'] = __jsl_clearance
            # response = session.get(url, headers=headers)
            a_cookies = requests.utils.dict_from_cookiejar(session.cookies)
            request.cookies = a_cookies


class RandomUserAgentMiddleware(object):
    """添加随机User—Agent"""

    def __init__(self, crawler):
        super(RandomUserAgentMiddleware, self).__init__()
        self.ua = UserAgent()
        self.ua_type = crawler.settings.get('RANDOM_UA_TYPE', 'random')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        def get_ua():
            """ Gets random UA based on the type setting (random, firefox…) """
            return getattr(self.ua, self.ua_type)

        request.headers.setdefault('User-Agent', get_ua())


class ProxyMiddleware(object):
    """ 设置Proxy"""

    def __init__(self, ip):
        self.session = requests.session()
        self.session.keep_alive = False
        self.ip = self.get_proxy(self.session)

    @staticmethod
    def get_proxy(session: Session()) -> str:
        """
        获取IP
        :return:代理ip
        """
        # session = requests.session()
        for i in range(10):
            ip = session.get("http://172.19.89.17:5010/get/")
            proxy = "http://" + ip.text
            proxies = {"http": "http://" + ip.text, "https": "https://" + ip.text}
            try:
                response = session.get('http://icanhazip.com/', proxies=proxies, timeout=1)
                proxyIP = response.text.strip()
                thisIP = ip.text[0:ip.text.rfind(":")].strip()
                if proxyIP == thisIP:
                    print("代理IP:'" + proxyIP + "'有效！")
                    return proxy
                else:
                    print("代理IP无效！")
            except:
                print("获取代理超时")

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        if self.ip:
            request.meta['proxy'] = self.ip
