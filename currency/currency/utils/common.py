import re
import hashlib
import requests
import urllib.parse
from w3lib import html
from bs4 import BeautifulSoup
from typing import List


def md5Hex(text_str: str, flag: bool = True) -> str:
    """
    文书号去除特殊字符再md5
    :param flag: 是否替换非中文和数字
    :param text_str: 文本
    :return: 加密字符
    """
    if flag:
        text_str = re.sub("[^a-zA-Z0-9\\u4e00-\\u9fa5]", "", text_str)
    m = hashlib.md5()
    m.update(text_str.encode("utf8"))
    return m.hexdigest()


def get_publisher(value: str) -> str:
    pat_dict = {'.*经.*信.*': 'econoAndInforCommittee', '.*工.*业.*': 'industrialBureau',
                '.*公.*路.*': 'highwayAdministration', '.*地.*震.*': 'seismologicalBureau',
                '.*金.*融.*': 'localFinanceSafety', '.*园.*林.*': 'gardenBureau', '.*食.*药.*': 'fdadministrative',
                '.*市.*场.*监督.*|.*监管.*': 'saows', '.*国.*科.*': 'nationalDefense', '.*广.*电.*': 'playBureau',
                '.*卫.*生.*|.*卫健.*': 'healthinspection', '.*科.*(学|技).*': 'science', '.*文.*旅.*': 'cttourism',
                '.*工.*信.*': 'boii', '.*文.*物.*': 'sach', '.*畜.*牧.*': 'husbandry', '.*无.*线.*电.*': 'radio',
                '.*烟.*草.*': 'tobacco', '.*邮.*政.*': 'postOffice', '.*审.*计.*': 'auditing', '.*公.*安.*': 'police',
                '.*农.*林.*': 'agriculture', '.*海.*事.*': 'msa', '.*经.*济.*|.*经外.*': 'economic', '.*民.*政.*': 'civilaffairs',
                '.*统.*计.*': 'statistical', '.*教.*育.*': 'bfeducation', '.*文.*体.*新.*': 'boc', '.*海.*渔.*': 'mfbureau',
                '.*体.*育.*': 'sport', '.*民.*局.*': 'civilDefence', '.*文.*体.*广.*新.*': 'snb', '.*房.*管.*': 'hpm',
                '.*物.*价.*': 'priceBureau', '.*水.*(利|务).*': 'water', '.*农.*(业|委|牧).*': 'geoponics',
                '.*规.*划.*': 'planning', '.*发.*改.*': 'ndrc', '.*人.*力.*': 'hr', '.*建.*设.*': 'construction',
                '.*商.*务.*': 'commercial', '.*旅.*游.*': 'tourism', '.*国.*税.*': 'nationalTax',
                '.*粮.*食.*': 'foodBureau', '.*司.*法.*': 'judiciary', '.*环.*保.*|.*环境.*': 'environmental', '.*税.*务.*': 'tax',
                '.*工.*商.*': 'business', '.*交.*通.*': 'traffic', '.*国.*土.*': 'land',
                '.*财.*政.*': 'finance', '.*文.*化.*': 'culture', '.*城.*管.*': 'urban', '.*林.*业.*': 'forestry',
                '.*住.*建.*': 'housing', '.*海.*关.*': 'customs', '.*卫.*计.*': 'health', '.*人.*民.*银.*行.*': 'CNbank',
                '.*保.*监.*': 'cricAdministrative', '.*银.*监.*': 'cbrcAdministrative', ".*人.*社.*": "hr", '.*自然资源.*': 'planAndNaturalBureau',
                '.*应急.*': 'emergencyBureau', '.*资源交易.*': 'publicTradingCenter', '.*市政.*': 'council', '.*国资.*': 'SASAC', '.*气象.*': 'weather',
                '.*信访.*': 'region_credit_office', '.*事务.*': 'utilityBureau'}
    for key in pat_dict.keys():
        if re.match(key, value):
            return pat_dict[key]


def is_not_empty(s: str) -> bool:
    """
    判断字符串是否为空
        print isNotEmpty("")    # False <br>
        print isNotEmpty("   ") # False <br>
        print isNotEmpty("ok")  # True  <br>
        print isNotEmpty(None)  # False <br>
    :param s: 字符串
    :return: 字符串为空返回False反之返回True
    """
    return bool(s and s.strip())


def reg_matching_text(reg: str, paragraph: str) -> str:
    """
    从文本中匹配必要字段
    :param reg: 正则
    :param paragraph:文本
    :return: 匹配到返回字段,反之返回空
    """
    text_value = ""
    if not reg.isspace():
        matcher = re.compile(reg).search(paragraph)
        if matcher:
            text_value = matcher.group()
            if text_value.find(":") > 0:
                text_value = text_value[text_value.index(":") + 1:].replace("</p>", "")

    return text_value


def extract_date(date_str: str) -> str:
    """
    用来获取文字中的日期
    :param date_str: 字符
    :return: 返回(yyyy-mm-dd)格式的日期
    """
    pattern = re.search(r"[129][\d]{3}[年/\-.][\d]{1,2}[月/\-.][\d]{1,2}", date_str)
    if pattern:
        # 正则,需要替换的字符,替换文本
        date_list = re.split("-", re.sub(r"[年月/.]", "-", pattern.group()))
        for index, date in enumerate(date_list):
            if len(date) == 1:
                date_list[index] = "0" + date
        # 拼接日期
        return "-".join(date_list)
    else:
        return ""


def chinese_date_parser(data_text: str) -> str:
    """
    中文日期替换
    :param data_text:
    :return: 返回yyyy-MM-dd格式日期
    """
    signs = {
        '一': '1', '壹': '1', '二': '2', '贰': '2', '貮': '2',
        '三': '3', '叁': '3', '四': '4', '肆': '4', '五': '5',
        '伍': '5', '六': '6', '陆': '6', '七': '7', '柒': '7',
        '八': '8', '捌': '8', '九': '9', '玖': '9', '〇': '0',
        '零': '0', 'o': '0', 'O': '0', 'ｏ': '0', 'Ｏ': '0',
        '○': '0', '①': '1', '②': '2', '③': '3', '④': '4',
        '⑤': '5', '⑥': '6', '⑦': '7', '⑧': '8', '⑨': '9'
    }
    for char in data_text:
        if signs.get(char):
            data_text = data_text.replace(char, signs.get(char))

    return extract_date(data_text)


def filter_tags(html_str: str, base_url: str, flag: bool = False) -> str:
    """
    获取正文
    :param html_str: 网页html
    :param base_url: 网页根路径
    :param flag: 是否拼接a或者img标签
    :return: 文本
    """
    global join
    # 为空返回
    if not is_not_empty(html_str):
        return ""

    keepTagNameList = ("div", "p", "br", "title", "thead", "tfoot", "th", "td", "tr", "a", "img")
    # 去掉HTML注释
    paragraph = re.compile('<!--[\s\S]*?-->').sub("", html_str)
    paragraph = re.compile(r'&nbsp;|&lt;|&gt;').sub("", paragraph)
    paragraph = html.remove_tags(paragraph, keep=keepTagNameList)
    paragraph = re.compile("\n").sub("", paragraph)
    paragraph = re.compile(r"(i)(s)<p\s+.*?>|<div(\s+.*?)?>|<h(\s+.*?)?>", re.IGNORECASE).sub("<p>", paragraph)
    paragraph = re.compile(r"<tr(\s+.*?)?>", re.IGNORECASE).sub("<p>", paragraph)
    paragraph = re.compile(r"</div>|</h\d>").sub("</p>", paragraph)
    paragraph = re.compile(r"</tr>", re.I).sub("</p>", paragraph)
    paragraph = re.compile(r"</?td(\s+.*?)?>", re.IGNORECASE).sub("", paragraph)
    paragraph = re.compile(r"</?br(\s+.*?)?>").sub("", paragraph)

    if flag:
        join = urljoin(paragraph, base_url)
        paragraph = join[2]
    else:
        paragraph = re.compile(r"\s").sub("", paragraph)

    paragraph = re.compile(r"\s").sub("", paragraph)

    # 替换p标签
    while paragraph.find("<p></p>") >= 0 or paragraph.find("<p><p>") >= 0 or paragraph.find("</p></p>") >= 0:
        paragraph = re.compile(r"<p></p>").sub("", paragraph)
        paragraph = re.compile(r"<p><p>").sub("<p>", paragraph)
        paragraph = re.compile(r"</p></p>").sub("</p>", paragraph)

    if not paragraph.startswith("<p>"):
        paragraph = "<p>" + paragraph

    if not paragraph.endswith("</p>"):
        paragraph = paragraph + "</p>"

    paragraph = re.compile(r"<p></p>").sub("", paragraph)
    # 替换实体
    if flag:
        for temp in join[0]:
            paragraph = re.compile(r"<flag-A>").sub(temp, paragraph, 1)

        for temp in join[1]:
            paragraph = re.compile(r"<flag-Img>").sub(temp, paragraph, 1)

    return paragraph


def urljoin(paragraph, base_url):
    # 定义标签正则
    a_pattern = re.compile(r"<a[^>]*href=[^>]*?>[^<]*</a>")
    img_pattern = re.compile(r"<img[^>]*src=[^>]*?>")
    complete_a_tag = []
    complete_img_tag = []

    # 转换为bs4对象
    str_tag = ''.join(a_pattern.findall(paragraph) + img_pattern.findall(paragraph))
    soup = BeautifulSoup(str_tag, "lxml")
    for tag in soup.select("a"):
        if tag.has_attr("href") and tag["href"]:
            tag["href"] = urllib.parse.urljoin(base_url, tag["href"])
            complete_a_tag.append(str(tag))

    for tag in soup.select("img"):
        if tag.has_attr("src") and tag["src"]:
            tag["src"] = urllib.parse.urljoin(base_url, tag["src"])
            complete_img_tag.append(str(tag))

    paragraph = a_pattern.sub("<flag-A>", paragraph)
    paragraph = img_pattern.sub("<flag-Img>", paragraph)

    return complete_a_tag, complete_img_tag, paragraph


def hash_value(data_list: List[dict], map_condition: dict, url: str):
    """
    生成adid和pid的方法
        相对应的传入三个参数:
           jsonObjects是dataList对象,
           mapCondition是条件Map对象,必需要传的参数有hashId,caseKey,idMatcher,contentKey;非必要穿的参数
               hashId:想要hash后的jsonObject的主键id名称,如行政处罚的adid.(必填)
               contentKey:jsonObject的文本内容,如行政处罚的paragraph的文本内容,String类型(必填)
               caseKey:jsonObject中的文号key.如行政处罚的identifier.(选填)
               idMatcher:匹配文号的正则(选填)
               urlIsAvailable:是否使用url来hash,若发现一定不能用url来hash,比如详情页链接带有随机数和的参数,则传入'no'字符串(选填)
        jsonObject内部的一个参数:
           idMethod:
               值为1:使用文号来hash的,
               值为2:使用url来hash的,
               值为3:使用文本内容来hash的.
    :param data_list: dataList对象
    :param map_condition: 条件map
    :param url:链接
    """

    if data_list is None or map_condition is None or url is None:
        raise RuntimeError("Parameter is null!")

    """
     获取要hashId的名称: key统一是hashId.必填项
     例如行政处罚: adid,
     行政许可: pid.
    """
    hashId = map_condition.get("hashId")
    if hashId is None:
        raise RuntimeError("Parameter hashId is Empty!")

    # 获取文本内容的key.必填项
    contentKey = map_condition.get("contentKey")
    if contentKey is None:
        raise RuntimeError("Parameter contentKey is Empty!")

    """
        取出文号值的key,从map中获取,key统一是case
        这样可以处理多种数据主体
    """

    caseKey = map_condition.get("caseKey")
    # 获取校验文号的正则值
    idMatcher = map_condition.get("idMatcher")

    for data in data_list:
        if data is None:
            continue
        # 获取地区编号
        regionCode = data.get("regionCode")

        identifier = ""
        if is_not_empty(caseKey):
            identifier = data.get(caseKey)
        # 若满足条件,优先hash文号;若不同地区之间文号雷同,则hash 文号+地区编码
        if is_not_empty(identifier) and is_not_empty(idMatcher):
            if re.match(idMatcher, identifier):
                # 若满足后,用正则,只保留中文,字母和数字
                if is_not_empty(regionCode):
                    data[hashId] = md5Hex(regionCode + "-" + identifier)
                else:
                    data[hashId] = md5Hex(identifier)
                data["idMethod"] = "1"
                continue
        """
            如满足条件,则hash url处罚许可冗余.
            urlIsAvailable是使用使用url来hash,
            一般情况下可以不传这个参数,但是发现实体页的url后面是带有随机数的参数,
            则要传该参数,值为'no'.
        """
        urlIsAvailable = map_condition.get("urlIsAvailable")
        url = url.strip()
        # 简单判断是否是合法的url地址
        urlCondition = r"(https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]"
        urlMatcher = re.match(urlCondition, url)
        if urlIsAvailable:
            if not urlIsAvailable == "no" and len(data) < 2:
                if urlMatcher:
                    data[hashId] = md5Hex(url, flag=False)
                    data["idMethod"] = "2"
                    continue
        else:
            if len(data) < 2:
                if urlMatcher:
                    data[hashId] = md5Hex(url, flag=False)
                    data["idMethod"] = "2"
                    continue

        # 以上条件不满足,则hash content
        if data.get(caseKey):
            raise RuntimeError("Parameter contentKey does not exist!")
        content = data.get(contentKey)
        if len(content) == 0:
            raise RuntimeError("JsonObject content is Empty!")

        if content:
            content = re.sub("\s*", "", str(content))
            data[hashId] = md5Hex(content)
            data["idMethod"] = "3"


def check_filed(fields, data_list: List):
    """
    校验必要字段
    :param fields: 需要校验的Set集合
    :param data_list: 数据列表
    :return: 如果data_list中某个字段名fields中不存在返回异常
    """
    for field in fields:
        for data_dict in data_list:
            if not data_dict.get(field):
                raise Exception(field + "字段缺失")


if __name__ == '__main__':
    print(md5Hex("123"))
    text = "<p>信息来源：凌河区法制办发布时间<p>：二〇一三年七月三十一日字体大小:小 中 大"
    print(chinese_date_parser(text))
