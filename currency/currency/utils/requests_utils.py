# author:胡已源
# datetime:2019/9/6 上午9:28
# software: PyCharm

import json
import time
import re
import requests
from urllib import parse

MAX_REQUEST = 10


class ProxyApiError(Exception):
    def __init__(self, api_url, url):
        self.errorMessage = "代理api错误,ip_host:{}".format(api_url)
        self.errorLink = url


class RequestError(Exception):
    def __init__(self, url):
        self.errorLink = url  # 错误链接',  # 访问失败的链接
        self.errorMessage = '请求html失败超过{}次,网络或者代理不稳定'.format(MAX_REQUEST)


def get_ip(ip_host, url):
    """
    :param ip_host: 代理的地址 目前为 http://172.19.89.17:5010
    :param url: 要请求的网址
    :return: 代理
    """
    s = requests.session()
    s.keep_alive = False
    try:
        proxy = s.get(ip_host + "/get/", timeout=15)
    except:
        raise ProxyApiError(ip_host, url)
    proxy = {'http': 'http://' + proxy.text.replace('\n', '').replace('\r', ''),
             'https': 'http://' + proxy.text.replace('\n', '').replace('\r', '')}
    return proxy


def request(method, url, ip_host, timeout=5, session=None, ts_before=0.0, ts_error=1, **kwargs):
    """封装requests
    method : get 或者 post
    url : 要请求的网址
    ip_host : 代理的地址 目前为 http://172.19.89.17:5010
    """
    if session:
        request_method = {'get': session.get, 'post': session.post}
    else:
        request_method = {'get': requests.get, 'post': requests.post}
    count = MAX_REQUEST
    proxy = get_ip(ip_host, url)
    while count > 0:
        try:
            time.sleep(ts_before)
            response = request_method[method](url, timeout=timeout, proxies=proxy, **kwargs)
            if response.status_code == 200 and response.text != '':
                return response
            else:
                print(response.status_code, '重新请求 ', url)
        except Exception:
            proxy = get_ip(ip_host, url)
            print("切换代理:", proxy)
            time.sleep(ts_error)

        count = count - 1

    raise RequestError(url)
