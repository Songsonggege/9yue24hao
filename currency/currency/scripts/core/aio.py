# author:胡已源
# datetime:2019/8/30 上午11:11
# software: PyCharm

import ssl
import aiohttp
from typing import Tuple, Optional, List, Union
from aiohttp import ClientSession, ClientResponse, FormData

"""
    aiohttp请求封装类
    官方文档：https://aiohttp.readthedocs.io/en/stable/client_quickstart.html
"""


async def fetch_get(
        session: ClientSession(),
        url: str,
        timeout: int = 10,
        headers: dict = None,
        cookies: dict = None,
        params: dict = None,
        proxy: dict = None
) -> Tuple[ClientResponse.text, ClientResponse.status, ClientResponse._headers]:
    """
    aiohttp异步的GET请求
    :param session: ClientSession()对象
    :param url: 需要解析的url
    :param timeout: 超时时间：单位秒
    :param headers:请求头不传入默认为None
    :param cookies: Cookie传入字典
    :param params:请求参数
    :param proxy: 代理IP
    :return: 返回文本内容和状态码
    """
    async with session.get(
            url,
            proxy=proxy,
            headers=headers,
            cookies=cookies,
            params=params,
            timeout=aiohttp.ClientTimeout(total=timeout),
            ssl=ssl.SSLContext()
    ) as response:
        return await response.text(), response.status, response.headers


async def fetch_post(
        session: ClientSession(),
        url: str,
        timeout: int = 20,
        headers: dict = None,
        cookies: dict = None,
        data: Union[dict, FormData()] = None,
        json_form: dict = None,
        proxy: dict = None
) -> Tuple[ClientResponse.text, ClientResponse.status, ClientResponse._headers]:
    #
    """
    aiohttp异步的POST请求
    :param session: session: ClientSession()对象
    :param cookies: cookie
    :param url: url: 需要解析的url
    :param timeout: timeout: 超时时间：单位秒
    :param data: 可以传入字典形势形式的参数,也可传入FormData()对象,用于文件类型的请求
    #https://aiohttp.readthedocs.io/en/stable/multipart.html
    :param json_form:
    :param headers: headers:请求头不传入默认为None
    :param proxy: 代理IP
    :return: 返回文本内容和状态码
    """
    async with session.post(
            url,
            proxy=proxy,
            headers=headers,
            cookies=cookies,
            data=data,
            json=json_form,
            timeout=aiohttp.ClientTimeout(total=timeout),
            ssl=ssl.SSLContext()
    ) as response:
        return await response.text(), response.status, response.headers
