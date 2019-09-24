import re
from typing import List

import requests
import traceback
import urllib.parse
from urllib.parse import urlparse
from w3lib import html as h, url as u
from bs4 import BeautifulSoup
from lxml import etree


def filter_tags(html_str: str) -> str:
    """
    获取正文
    :param html_str: 网页html
    :return: 文本
    """
    # 为空返回
    if not bool(html_str and html_str.strip()):
        return ""

    keep_tag_list = ("div", "p", "br", "title", "thead", "tfoot", "th", "td", "tr")
    paragraph = h.remove_comments(html_str)
    paragraph = h.replace_entities(paragraph)
    paragraph = h.remove_tags(paragraph, keep=keep_tag_list)
    paragraph = h.replace_escape_chars(paragraph)
    paragraph = re.sub(r"(?i)(?s)<(tr|p|div)(\s+.*?)?>", "<p>", paragraph)
    paragraph = re.sub(r"(?i)(?s)</(div|tr)>", "</p>", paragraph)
    paragraph = re.sub(r"(?i)(?s)</?td(\s+.*?)?>", "", paragraph)
    paragraph = re.sub(r"(<br>)+|<br/>", "<br>", paragraph)
    paragraph = re.sub(r"【打印本页】", "", paragraph)
    paragraph = re.sub(r"【关闭窗口】", "", paragraph)
    paragraph = re.sub(r"\s", "", paragraph)

    if paragraph.count("<br>") > 0:
        temp = ""
        for item in paragraph.split("<br>"):
            temp = temp + "<p>" + item + "</p>"
        paragraph = temp

    if not paragraph.startswith("<p>"):
        paragraph = "<p>" + paragraph

    if not paragraph.endswith("</p>"):
        paragraph = paragraph + "</p>"

    # 替换p标签
    while "<p></p>" in paragraph or "<p><p>" in paragraph or "</p></p>" in paragraph:
        paragraph = re.sub(r"<p></p>", "", paragraph)
        paragraph = re.sub(r"<p><p>", "<p>", paragraph)
        paragraph = re.sub(r"</p></p>", "</p>", paragraph)

    return paragraph


def get_urls_from_text(html_: str, base_url: str) -> dict:
    """
    返回文本中所有的a标签
    :param html_: html
    :param base_url: 网页根路径
    :return: 返回字典类型key为url，value为url的文本
    """
    try:
        urls: dict = {}
        soup = BeautifulSoup(html_, 'lxml')  # 文档对象
        # 查找文档中所有a标签
        for element in soup.find_all('a'):
            link = element.get('href')

            if not valid_link(element):
                continue

            if len(link) > 9:
                base_link = urllib.parse.urljoin(
                    u.safe_url_string(base_url),
                    u.safe_url_string(link, encoding='utf-8')
                )
                urls[base_link] = element.get_text(strip=True)
        return urls
    except:
        print("从网页中提取 a 标签 href 出错", traceback.format_exc())


def get_images(html_: str, base_url: str) -> List[str]:
    """
    获取网页中所有的img
    :param html_: html
    :param base_url: 网页根路径
    :return: 返回列表
    """
    try:
        url_set = set()
        soup = BeautifulSoup(html_, 'lxml')  # 文档对象
        for element in soup.find_all('img'):
            url = element.get("src")
            if url and url.strip() and len(url) > 9:
                base_link = urllib.parse.urljoin(
                    u.safe_url_string(base_url),
                    u.safe_url_string(url, encoding='utf-8')
                )
                url_set.add(base_link)
        return list(url_set)
    except:
        print("从网页中提取 img 标签 src 出错", traceback.format_exc())


def is_file_url(file_url: str) -> bool:
    """
    判断是否为图片
    :param file_url:文件url
    :return: 是文件类型返回True反之
    """
    file_url = file_url.lower()
    if file_url.endswith(".pdf") or file_url.endswith(".zip") or file_url.endswith(".xls") or file_url.endswith(".xlsx") or file_url.endswith(".doc") or file_url.endswith(".docx"):
        return True
    return False


def get_domain(url: str):
    """
    获取url的域名
    :param url: url地址
    :return: 返回url的协议和域名
    """
    res = urlparse(url)
    print("返回对象：", res)
    return res.scheme + "://" + res.netloc


def valid_link(element):
    href = element.get("href")
    if not href:
        return False
    if "#" in href or "/" == href or "javascript" in href:
        return False
    if element and len(element.get("onclick")) > 0:
        return False
    return True


def format_cookie(cookies_str: str) -> dict:
    """
    从浏览器中的cookies转换为字典
    :param cookies_str: 字符串
    :return: 字典cookies
    """
    find = re.findall(r'(\S+)=(\S+)(?:$|;)', cookies_str)
    return dict(find)


if __name__ == '__main__':
    url_ = "http://xxgk.deyang.gov.cn/xxgkml/detail01.jsp?id=20190201164037-738523-00-000"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36"
    }
    response = requests.get(url_, headers=headers)

    # 进行过滤

    text = response.content.decode('utf-8')
    html = etree.HTML(text)
    str_html = etree.tostring(html.xpath("//div[@id='info_content']")[0], encoding='utf-8').decode()
    print(type(str_html))
    print(filter_tags(str_html))
