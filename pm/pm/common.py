# coding: utf-8
import hashlib
import re
import time
from w3lib import html
from bs4 import BeautifulSoup
import urllib.parse
import requests
from lxml import etree
from datetime import datetime, timedelta


sales_status_dict = {'0': '即将开始', '1': '正在拍卖', '2': '已流拍', '3': '已成交',  '4': '已中止', '5': '已撤回', '6': '已暂缓'}
auction_phase_dict = {'1': '一拍', '2': '二拍', '3': '变卖'}
bidding_record_dict = {0: '成交', 1: '出局'}
taobao_bidding_record_dict = {99: '成交', -1: '出局'}

taobao_sales_status_dict = {'todo': '即将开始', 'doing': '正在拍卖', 'done': '已成交', 'failure': '已流拍',  'break': '已中止', 'revocation': '已撤回'}


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


def filter_tags(html_str: str, base_url: str, flag: bool = False) -> str:
    """
    获取正文
    :param html_str: 网页html
    :param base_url: 网页根路径
    :param flag: 是否拼接a或者img标签
    :return: 文本
    """
    # global join
    join = ()
    keepTagNameList = ("div", "p", "br", "title", "thead", "tfoot", "th", "td", "tr", "a", "img")

    # 去掉HTML注释
    paragraph = re.compile('<!--[\s\S]*?-->').sub("", html_str)
    paragraph = re.compile(r'&nbsp;|&lt;|&gt;').sub("", paragraph)
    paragraph = html.remove_tags(paragraph, keep=keepTagNameList)
    paragraph = re.compile("\n").sub("", paragraph)
    paragraph = re.compile(r"<p\s+.*?>|<div(\s+.*?)?>", re.IGNORECASE).sub("<p>", paragraph)
    paragraph = re.compile(r"<tr(\s+.*?)?>", re.IGNORECASE).sub("", paragraph)
    paragraph = re.compile(r"</div>").sub("</p>", paragraph)
    paragraph = re.compile(r"</tr>", re.I).sub("", paragraph)
    paragraph = re.compile(r"<td\s+.*?>", re.IGNORECASE).sub("<p>", paragraph)
    paragraph = re.compile(r"</td>", re.IGNORECASE).sub("</p>", paragraph)
    # paragraph = re.compile(r"</?br(\s+.*?)?>").sub("", paragraph)

    if flag:
        join = urljoin(paragraph, base_url)
        paragraph = join[2]
    # paragraph = re.compile(r"\s").sub("", paragraph)
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


def type1(i):
    pat_dict = {
                '376': '房产', '381': '土地',  '385': '无形资产', '382': '财产性权益',
                '386': '林权矿权', '379': '其他', '372': '股权', '378': '机动车',
                '383': '船舶', '377': '物资', '380': '工艺品',
                 }
    for key in pat_dict.keys():
        if (re.match("{}".format(key), i)):
            type = pat_dict[key]
            return type


def sales_status1(i):
    pat_dict = {
                '2': '正在拍卖', '1': '即将开始',  '3': '已成交', '4': '其他',
                 }
    for key in pat_dict.keys():
        if (re.match("{}".format(key), i)):
            type = pat_dict[key]
            return type


def deal_date(values):
    """
    对数字时间类型的字符串进行处理，返回为标准时间类型的字符串（如‘yyyy-mm-dd’）或者空‘’，
    values：string类型
    """
    try:
        if values == '':
            return ''
        values = values.replace('\xa0', '').replace(' ', '')
        date_temp = []
        if '.' in values:
            date_temp = values.split('.')

        elif '/' in values:
            date_temp = values.split('/')

        elif re.findall('(\d{4})年(\d+)月(\d+)日', values) != []:
            date_temp1 = re.findall('(\d{4})年(\d+)月(\d+)日', values)
            date_temp = date_temp1[0]

        elif re.findall('(\d{4})-(\d+)-(\d+)', values) != []:
            date_temp1 = re.findall('(\d{4})-(\d+)-(\d+)', values)
            date_temp = date_temp1[0]

        elif len(values) == 8 and values.isdigit():
            date_temp = [values[:4], values[4:6], values[6:8]]

        else:
            return ''

        month = date_temp[1]
        if len(date_temp[1]) == 1:
            month = '0' + date_temp[1]
        day = date_temp[2]
        if len(date_temp[2]) == 1:
            day = '0' + date_temp[2]
        return date_temp[0] + '-' + month + '-' + day
    except:
        print('')
        return ''


def get_id(text):  # flag 1 表示文号 0 表示其他
    """//*[@id="testUI"]/tbody/tr[28]
    文书号去除特殊字符再md5
    :param text:
    :return :
    """
    text = re.sub("[^a-zA-Z0-9\\u4e00-\\u9fa5]", "", text)
    m = hashlib.md5()
    m.update(text.encode("utf8"))
    return m.hexdigest()


def to_time_str(timestamp):
    # timestamp = 1381419600
    time_array = time.localtime(timestamp)
    # print(time_array)
    time_str = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
    # start_date = time.strftime("%Y-%m-%d", time_array)
    # print(start_date)
    return time_str


def to_timestamp(time_str):
    # time_str = "2013-10-10 23:40:00"
    time_array = time.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    # print(time_array)
    timestamp = int(time.mktime(time_array))
    # print(timestamp)
    return timestamp


def upload_file(url):
    try:
        m = hashlib.md5()
        m.update(url.encode('utf-8'))
        url_md5 = m.hexdigest()
        # print(url_md5, 111)
        # hdfs_url = "/v1/sitesTest/sf.caa123.org.cn/{}/?op=CREATE&overwrite=true&user.name=hdfs".format(url_md5)
        # hdfs_url = "http://172.16.20.2:50070/webhdfs/v1/sitesTest/sf.caa123.org.cn/{}/?op=CREATE&overwrite=true&user.name=hdfs".format(url_md5)
        hdfs_url = "http://172.16.20.2:50070/webhdfs/v1/sites/sf.caa123.org.cn/{}/?op=CREATE&overwrite=true&user.name=hdfs".format(url_md5)
        resp = requests.put(hdfs_url, allow_redirects=False, timeout=60)
        url_location = resp.headers['Location'].replace(re.findall('http://(.*?)/', resp.headers['Location'])[0], '172.16.20.2:50075')
        file_resp = requests.get(url, timeout=60)
        resp = requests.put(url_location, data=file_resp.content, timeout=60)
        if resp.status_code == 201 and resp.headers['Content-Length'] == '0':
            print(url, '上传附件成功！！！')
            # return 1
            return url_md5
        else:
            print(url, "上传附件失败!!!")
            return 0
    except:
        print(url, "没有附件")
        return 2


# 解析表格
def extract_table(html_str):
    result_list = []
    result_dict = {}
    # delete_index_list = []
    # simple_tr_list = []
    html_tree = etree.HTML(html_str)
    table = html_tree.xpath('//table')
    if not table:
        return
    # etree.tostring(table, encoding='utf-8').decode()  # 获取html内容，包含标签
    # tree.xpath("string(/)")  # 获取文本内容，不包含标签
    tr_list = table[0].xpath('.//tr')
    tr_list_len = len(tr_list)
    # print(len(tr_list))
    total_tr_set = set(range(len(tr_list)))
    complicated_tr_set = set()
    # print(total_tr_set)

    index_and_len = []
    for index, tr in enumerate(tr_list):
        td_list = tr.xpath('.//td')
        if td_list:
            rowspan = td_list[0].xpath('./@rowspan')
            if rowspan:
                rows = int(rowspan[0])
                if index + rows <= tr_list_len:
                    index_and_len.append([index, rows])
    # print(index_and_len)

    if index_and_len:
        for index, rows in index_and_len:
            td_str_list = []
            for tr in tr_list[index: index + rows]:
                td_list = tr.xpath('.//td')
                for each_td in td_list:
                    td_str = each_td.xpath("string(.)")
                    td_str_list.append('<p>{}</p>'.format(td_str))
            # print(td_str_list)
            key = td_str_list[0]
            # value = '，'.join(td_str_list[1:]) if len(td_str_list) > 1 else ''
            value = ''.join(td_str_list[1:]) if len(td_str_list) > 1 else ''
            result_dict.update({key: value})
            # result_list.append('<p>{}</p>'.format(key))
            # result_list.append('<p>{}</p>'.format(value))
            result_list.append(key)
            result_list.append(value)

            for i in range(index, index + rows):
                # delete_index_list.append(i)
                complicated_tr_set.add(i)

        total_tr_set = total_tr_set.difference(complicated_tr_set)

    # print(total_tr_set)

    for i in total_tr_set:
        td_list = tr_list[i].xpath('.//td')
        td_str_list = []
        for each_td in td_list:
            td_str = each_td.xpath("string(.)")
            td_str_list.append('<p>{}</p>'.format(td_str))

        key = td_str_list[0].replace('<p>', '').replace('</p>', '')
        # value = '，'.join(td_str_list[1:]) if len(td_str_list) > 1 else ''
        value = ''.join(td_str_list[1:]) if len(td_str_list) > 1 else ''
        result_dict.update({key: value})
        # result_list.append('<p>{}</p>'.format(key))
        # result_list.append('<p>{}</p>'.format(value))
        result_list.append(key)
        result_list.append(value)

    # print(len(tr_list))
    # print(result_list)
    # print(result_dict)
    return result_dict


def extract_table_new(html_str):
    result_list = []
    result_dict = {}
    # delete_index_list = []
    # simple_tr_list = []
    html_tree = etree.HTML(html_str.replace("\\", ""))
    table = html_tree.xpath('//table')
    if not table:
        return {}, []
    # etree.tostring(table, encoding='utf-8').decode()  # 获取html内容，包含标签
    # tree.xpath("string(/)")  # 获取文本内容，不包含标签
    tr_list = table[0].xpath('.//tr')
    tr_list_len = len(tr_list)
    # print(len(tr_list))
    total_tr_set = set(range(len(tr_list)))
    complicated_tr_set = set()
    # print(total_tr_set)

    index_and_len = []
    for index, tr in enumerate(tr_list):
        td_list = tr.xpath('.//td')
        if td_list:
            if td_list[0].xpath('string(.)').strip():
                rowspan = td_list[0].xpath('./@rowspan')
                if rowspan:
                    rows = int(rowspan[0])
                    if index + rows <= tr_list_len:
                        index_and_len.append([index, rows])
    # print(index_and_len)

    if index_and_len:
        for index, rows in index_and_len:
            td_str_list = []
            for tr in tr_list[index: index + rows]:
                td_list = tr.xpath('.//td')
                for each_td in td_list:
                    # td_str = each_td.xpath("string(.)")
                    # td_str_list.append('<p>{}</p>'.format(td_str))
                    td_str = filter_tags(etree.tostring(each_td, encoding='utf-8').decode().replace('\xa0', ''), '')
                    td_str_list.append(td_str)
            # print(td_str_list)
            key = td_str_list[0]
            # value = '，'.join(td_str_list[1:]) if len(td_str_list) > 1 else ''
            value = ''.join(td_str_list[1:]) if len(td_str_list) > 1 else ''
            result_dict.update({key: value})
            # result_list.append('<p>{}</p>'.format(key))
            # result_list.append('<p>{}</p>'.format(value))
            result_list.append(key)
            result_list.append(value)

            for i in range(index, index + rows):
                # delete_index_list.append(i)
                complicated_tr_set.add(i)

        total_tr_set = total_tr_set.difference(complicated_tr_set)

    # print(total_tr_set)

    for i in total_tr_set:
        td_list = tr_list[i].xpath('.//td')
        td_str_list = []
        for each_td in td_list:
            # td_str = each_td.xpath("string(.)")
            # td_str_list.append('<p>{}</p>'.format(td_str))
            td_str = filter_tags(etree.tostring(each_td, encoding='utf-8').decode().replace('\xa0', ''), '')
            td_str_list.append(td_str)

        # if td_str_list:
        #     key = td_str_list[0].strip()
        #     if key:
        #         # value = '，'.join(td_str_list[1:]) if len(td_str_list) > 1 else ''
        #         value = ''.join(td_str_list[1:]) if len(td_str_list) > 1 else ''
        #     else:
        #         key = td_str_list[1].strip()
        #         value = ''.join(td_str_list[2:]) if len(td_str_list) > 2 else ''
        #
        #     result_dict.update({key: value})
        #     # result_list.append('<p>{}</p>'.format(key))
        #     # result_list.append('<p>{}</p>'.format(value))
        #     result_list.append(key)
        #     result_list.append(value)

        if td_str_list:
            td_str_list_len = len(td_str_list)
            for index, each_p in enumerate(td_str_list):
                if each_p.strip():
                    key = each_p
                    if index >= td_str_list_len - 1:
                        value = ''
                    else:
                        value = ''.join(td_str_list[index + 1])

                    result_dict.update({key: value})
                    # result_list.append('<p>{}</p>'.format(key))
                    # result_list.append('<p>{}</p>'.format(value))
                    result_list.append(key)
                    result_list.append(value)
                    break

    # print(len(tr_list))
    # print(result_list)
    # print(result_dict)
    return result_dict, result_list


def date_offset(start_date, days=30):
    d = datetime.strptime(start_date, '%Y-%m-%d')
    d1 = d + timedelta(days=days)
    return str(d1).split()[0]


def get_field_info(table_dict, table_list):
    field_info_dict = {}
    relation = get_info_from_dict(table_dict, ['所有人', '产权人为?', '所有权人']).replace('<p>', '').replace('</p>', '')
    field_info_dict['relation'] = [relation] if relation else []
    field_info_dict['disposal_basis'] = get_info_from_dict(table_dict, ['权利来源', '处置依据', '拍卖依据']).replace('<p>', '').replace('</p>', '')
    field_info_dict['authority_card'] = get_info_from_dict(table_dict, ['权证情况']).replace('<p>', '').replace('</p>', '')
    field_info_dict['sales_actuality'] = get_info_from_dict(table_dict, ['现状'])
    # field_info_dict['sales_actuality'] = '<p>{}</p>'.format(sales_actuality) if sales_actuality else ''
    field_info_dict['restriction_of_rights'] = get_info_from_dict(table_dict, ['权利限制'])
    # field_info_dict['restriction_of_rights'] = '<p>{}</p>'.format(restriction_of_rights) if restriction_of_rights else ''
    field_info_dict['clinch_deal_file'] = get_info_from_dict(table_dict, ['提供的?文件'])
    # field_info_dict['clinch_deal_file'] = '<p>{}</p>'.format(clinch_deal_file) if clinch_deal_file else ''

    # lots_introduce = self.get_info_from_dict(table_dict, ['标的物?介绍', '拍品介绍', '标的情况', '标的物基本信息'])
    # field_info_dict['lots_introduce'] = '<p>{}</p>'.format(lots_introduce) if lots_introduce else ''
    field_info_dict['lots_introduce'] = ''
    for k, v in table_dict.items():
        # if re.search('|'.join(['标的物?介绍', '拍品介绍', '标的情况', '标的物基本信息']), k):
        if re.search('|'.join(['标的物?介绍', '拍品介绍']), re.sub('\s', '', k)):
            if v.strip():
                field_info_dict['lots_introduce'] = v.strip()
            else:
                lots_introduce = ''
                len_table_list = len(table_list)
                for index, each_p in enumerate(table_list):
                    # m = re.search('<p>.*?(标的物?介绍|拍品介绍|标的情况|标的物基本信息).*?</p>', each_p)
                    m = re.search('<p>.*?(标的物?介绍|拍品介绍).*?</p>', re.sub('\s', '', each_p))
                    if m:
                        # m1 = re.search('<p>.*?(标的物?介绍|拍品介绍|标的情况|标的物基本信息).*?</p>(<p>.*</p>)', each_p)
                        m1 = re.search('<p>.*?(标的物?介绍|拍品介绍).*?</p>(<p>.*</p>)', re.sub('\s', '', each_p))
                        # m2 = re.search('(<p>.*?(标的物?介绍|拍品介绍).*</p>)', re.sub('\s', '', each_p))
                        if m1:
                            lots_introduce = m1.group(2)
                        # elif m2:
                        #     lots_introduce = m2.group(1)
                        else:
                            if index >= len_table_list - 1:
                                lots_introduce = ''
                            else:
                                for a in table_list[index + 1:]:
                                    if a.strip():
                                        lots_introduce = a.strip()
                                        break
                        break
                field_info_dict['lots_introduce'] = lots_introduce
            break

    return field_info_dict


def get_info_from_dict(table_dict, keywords):
    # keywords 是 ['所有人', '产权人为', '所有权人']
    # print('|'.join(keywords))
    for k, v in table_dict.items():
        if re.search('|'.join(keywords), re.sub('\s', '', k)):
            return v.strip()
    return ''


if __name__ == '__main__':
    # table = """<table border=\\\'1\\\' cellpadding=\\\'0\\\' cellspacing=\\\'0\\\' style=\\\'border-collapse: collapse;width: 100%;\\\'><tr><td class=\\\'auction-table-header\\\' colspan=\\\'4\\\'>开采/勘探矿权标的调查情况表</td></tr><tr><td class=\\\'auction-table-label\\\'>标的名称</td><td class=\\\'auction-table-value\\\' colspan=\\\'3\\\'>准格尔旗尔林兔煤炭有限责任公司煤矿采矿权1个</td></tr><tr><td class=\\\'auction-table-label\\\' rowspan=\\\'2\\\'>权证情况</td><td class=\\\'auction-table-label\\\'>法院执行裁定书</td><td class=\\\'auction-table-value\\\' colspan=\\\'2\\\'>&nbsp;</td></tr><tr><td class=\\\'auction-table-label\\\'>采矿许可证/矿产资源勘测许可证</td><td class=\\\'auction-table-value\\\' colspan=\\\'2\\\'>C1500002009051120016226</td></tr><tr><td class=\\\'auction-table-label\\\'>标的所有人</td><td class=\\\'auction-table-value\\\' colspan=\\\'3\\\'>准格尔旗尔林兔煤炭有限责任公司</td></tr><tr><td class=\\\'auction-table-label\\\'>评估鉴定基准日</td><td class=\\\'auction-table-value\\\' colspan=\\\'3\\\'>2019年4月30日</td></tr><tr><td class=\\\'auction-table-label\\\' rowspan=\\\'4\\\'>标的现状</td><td class=\\\'auction-table-label\\\'>财产用途及土地性质</td><td class=\\\'auction-table-value\\\' colspan=\\\'2\\\'>采矿权</td></tr><tr><td class=\\\'auction-table-label\\\'>租赁情况</td><td class=\\\'auction-table-value\\\' colspan=\\\'2\\\'>无出租</td></tr><tr><td class=\\\'auction-table-label\\\'>钥匙</td><td class=\\\'auction-table-value\\\' colspan=\\\'2\\\'>无</td></tr><tr><td class=\\\'auction-table-label\\\'>配套情况</td><td class=\\\'auction-table-value\\\' colspan=\\\'2\\\'>&nbsp;</td></tr><tr><td class=\\\'auction-table-label\\\' rowspan=\\\'2\\\'>权利限制情况</td><td class=\\\'auction-table-label\\\'>查封</td><td class=\\\'auction-table-value\\\' colspan=\\\'2\\\'>无</td></tr><tr><td class=\\\'auction-table-label\\\'>抵押</td><td class=\\\'auction-table-value\\\' colspan=\\\'2\\\'>无抵押</td></tr><tr><td class=\\\'auction-table-label\\\'>提供的文件</td><td class=\\\'auction-table-value\\\' colspan=\\\'3\\\'>1、《法院裁定书》；2、《协助执行通知书》；\\\n3、《拍卖成交确认书》4、其他</td></tr><tr><td class=\\\'auction-table-label\\\' rowspan=\\\'9\\\'>标的物介绍</td><td class=\\\'auction-table-label\\\'>所在地点</td><td class=\\\'auction-table-value\\\' colspan=\\\'2\\\'>鄂尔多斯市准格尔旗曹羊线32公里</td></tr><tr><td class=\\\'auction-table-label\\\'>勘查面积</td><td class=\\\'auction-table-value\\\' colspan=\\\'2\\\'>&nbsp;</td></tr><tr><td class=\\\'auction-table-label\\\'>矿山名称</td><td class=\\\'auction-table-value\\\' colspan=\\\'2\\\'>准格尔旗尔林兔煤炭有限责任公司煤矿</td></tr><tr><td class=\\\'auction-table-label\\\'>矿区面积</td><td class=\\\'auction-table-value\\\' colspan=\\\'2\\\'>7.2381平方公里</td></tr><tr><td class=\\\'auction-table-label\\\'>开采矿种</td><td class=\\\'auction-table-value\\\' colspan=\\\'2\\\'>煤炭</td></tr><tr><td class=\\\'auction-table-label\\\'>开采方式</td><td class=\\\'auction-table-value\\\' colspan=\\\'2\\\'>露天开采</td></tr><tr><td class=\\\'auction-table-label\\\'>生产规模</td><td class=\\\'auction-table-value\\\' colspan=\\\'2\\\'>60万吨/年</td></tr><tr><td class=\\\'auction-table-label\\\'>可采储量</td><td class=\\\'auction-table-value\\\' colspan=\\\'2\\\'>3153万吨</td></tr><tr><td class=\\\'auction-table-label\\\'>采矿/勘探许可证有效期</td><td class=\\\'auction-table-value\\\' colspan=\\\'2\\\'>2019年12月31日</td></tr><tr><td class=\\\'auction-table-label\\\' rowspan=\\\'7\\\'>标的物估值</td><td class=\\\'auction-table-label\\\'>标的评估总价</td><td class=\\\'auction-table-value\\\' colspan=\\\'2\\\'>82510.21万元</td></tr><tr><td class=\\\'auction-table-label\\\'>费用总价</td><td class=\\\'auction-table-value\\\' colspan=\\\'2\\\'>&nbsp;</td></tr><tr><td class=\\\'auction-table-label\\\' rowspan=\\\'4\\\'>税费（买受人承担）</td><td class=\\\'auction-table-value\\\' colspan=\\\'2\\\'>营业税：  以税务机关要求为准</td></tr><tr><td class=\\\'auction-table-value\\\' colspan=\\\'2\\\'>土地增值税：以税务机关要求为准</td></tr><tr><td class=\\\'auction-table-value\\\' colspan=\\\'2\\\'>印花税：以税务机关要求为准</td></tr><tr><td class=\\\'auction-table-value\\\' colspan=\\\'2\\\'>个人所得税：以税务机关要求为准</td></tr><tr><td class=\\\'auction-table-label\\\'>其他费用情况</td><td class=\\\'auction-table-value\\\' colspan=\\\'2\\\'>采矿权价款：569万元\\\n矿山地质环境治理恢复保证金415.818万元\\\n</td></tr></table><p class="structured-splitor"></p>"""
    table = "<table><tbody><tr style='HEIGHT: 28px' class='firstRow'><td style='BORDER-BOTTOM: #f0f0f0; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; WORD-BREAK: break-all; BORDER-TOP: #f0f0f0; BORDER-RIGHT: #f0f0f0; PADDING-TOP: 0px' width='613' colspan='6'><p style='TEXT-ALIGN: center; TEXT-INDENT: 36px'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 21px'>司法车辆标的物情况调查表</span></strong></p></td></tr><tr style='HEIGHT: 21px'><td style='BORDER-BOTTOM: #f0f0f0; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: #f0f0f0; PADDING-TOP: 0px' width='68'></td><td style='BORDER-BOTTOM: #f0f0f0; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: #f0f0f0; PADDING-TOP: 0px' width='149'></td><td style='BORDER-BOTTOM: #f0f0f0; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: #f0f0f0; PADDING-TOP: 0px' width='161'></td><td style='BORDER-BOTTOM: #f0f0f0; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: #f0f0f0; PADDING-TOP: 0px' width='62'></td><td style='BORDER-BOTTOM: #f0f0f0; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: #f0f0f0; PADDING-TOP: 0px' width='173' colspan='2'></td></tr><tr style='HEIGHT: 27px'><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: windowtext 1px solid; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: windowtext 1px solid; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='68'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>拍卖标的名称</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: windowtext 1px solid; BORDER-RIGHT: #f0f0f0; PADDING-TOP: 0px' width='149'><p style='TEXT-ALIGN: left'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>沪HJ9220北京现代牌小型轿车</span></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: windowtext 1px solid; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: windowtext 1px solid; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='161'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>案  号</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: windowtext 1px solid; BORDER-RIGHT: black 1px solid; PADDING-TOP: 0px' width='235' colspan='3'><p style='TEXT-ALIGN: left'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>（2017）沪0106执恢881号</span></p></td></tr><tr style='HEIGHT: 21px'><td style='BORDER-BOTTOM: black 1px solid; BORDER-LEFT: windowtext 1px solid; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' rowspan='10' width='68'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>标的物登记信息</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='149'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>财产所有人</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='161'><p style='TEXT-ALIGN: left'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>上海丰勤物流有限公司</span></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='65' colspan='2'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 15px'>号牌种类</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='169'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>小型汽车</span></p></td></tr><tr style='HEIGHT: 20px'><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='149'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>机动车登记编号</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='161'><p style='TEXT-ALIGN: left'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>310001847738</span></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='65' colspan='2'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>车辆类型</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='169'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>小型轿车</span></p></td></tr><tr style='HEIGHT: 19px'><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='149'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>车辆品牌</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='161'><p style='TEXT-ALIGN: left'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>北京现代牌</span></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='65' colspan='2'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>发动机号</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='169'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>9B174435</span></p></td></tr><tr style='HEIGHT: 27px'><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='149'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>车辆识别号</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='161'><p style='TEXT-ALIGN: left'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>LBEXDAEB29X746132</span></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='65' colspan='2'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>车辆型号</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='169'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>BH7162MX</span></p></td></tr><tr style='HEIGHT: 25px'><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; WORD-BREAK: break-all; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='149'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>车牌号</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='161'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>沪HJ9220</span></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='65' colspan='2'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>注册登记日期</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='169'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>2009-6-23</span></p></td></tr><tr style='HEIGHT: 20px'><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='149'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>出厂日期</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='161'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>2009-5-14</span></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='65' colspan='2'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>使用性质</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='169'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>非营运</span></p></td></tr><tr style='HEIGHT: 19px'><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='149'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>车身颜色</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='161'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>黑</span></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='65' colspan='2'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>机动车状况</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='169'><p style='TEXT-ALIGN: left'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>违法未处理、查封、逾期未检验</span></p></td></tr><tr style='HEIGHT: 20px'><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='149'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>是否年审</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='161'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>否</span></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; WORD-BREAK: break-all; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='65' colspan='2'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>表显里程</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; WORD-BREAK: break-all; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='169'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>不详</span></p></td></tr><tr style='HEIGHT: 20px'><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='149'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>年检到期</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; WORD-BREAK: break-all; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='161'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>不祥</span></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='65' colspan='2'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>排量</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; WORD-BREAK: break-all; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='169'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>1599ML 82KW</span></p></td></tr><tr style='HEIGHT: 21px'><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='149'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>其他特别情况说明</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; WORD-BREAK: break-all; BORDER-TOP: #f0f0f0; BORDER-RIGHT: black 1px solid; PADDING-TOP: 0px' width='395' colspan='4'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>　</span></p></td></tr><tr style='HEIGHT: 19px'><td style='BORDER-BOTTOM: #f0f0f0; BORDER-LEFT: windowtext 1px solid; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' rowspan='2' width='68'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>标的物证照情况</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='149'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>车辆登记证</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; WORD-BREAK: break-all; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='161'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>无</span></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; WORD-BREAK: break-all; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='65' colspan='2'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>行驶证</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; WORD-BREAK: break-all; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='169'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>有</span></p></td></tr><tr style='HEIGHT: 19px'><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='149'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>购置证</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; WORD-BREAK: break-all; BORDER-TOP: #f0f0f0; BORDER-RIGHT: #f0f0f0; PADDING-TOP: 0px' width='161'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>无</span></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; WORD-BREAK: break-all; BORDER-TOP: #f0f0f0; BORDER-RIGHT: #f0f0f0; PADDING-TOP: 0px' width='65' colspan='2'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>　</span></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; WORD-BREAK: break-all; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='169'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>　</span></p></td></tr><tr style='HEIGHT: 19px'><td style='BORDER-BOTTOM: black 1px solid; BORDER-LEFT: windowtext 1px solid; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: windowtext 1px solid; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' rowspan='2' width='68'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>车辆状态</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='149'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>违章</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; WORD-BREAK: break-all; BORDER-TOP: #f0f0f0; BORDER-RIGHT: black 1px solid; PADDING-TOP: 0px' width='395' colspan='4'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>至少2个违章，罚款400元</span></p></td></tr><tr style='HEIGHT: 19px'><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='149'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>查封</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; WORD-BREAK: break-all; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='161'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>是</span></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; WORD-BREAK: break-all; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='65' colspan='2'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>抵押或质押</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='169'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>无</span></p></td></tr><tr style='HEIGHT: 24px'><td style='BORDER-BOTTOM: black 1px solid; BORDER-LEFT: windowtext 1px solid; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' rowspan='4' width='68'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>看样情况</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='149'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>车况说明</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; WORD-BREAK: break-all; BORDER-TOP: #f0f0f0; BORDER-RIGHT: black 1px solid; PADDING-TOP: 0px' width='395' colspan='4'></td></tr><tr style='HEIGHT: 21px'><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='149'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>看样地址</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; WORD-BREAK: break-all; BORDER-TOP: #f0f0f0; BORDER-RIGHT: black 1px solid; PADDING-TOP: 0px' width='395' colspan='4'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>上海市静安区康定路1097号上海市静安区人民法院后面停车场</span></p></td></tr><tr style='HEIGHT: 21px'><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='149'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>看样联系人</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; WORD-BREAK: break-all; BORDER-TOP: #f0f0f0; BORDER-RIGHT: #f0f0f0; PADDING-TOP: 0px' width='161'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>刘先生</span></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: windowtext 1px solid; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='65' colspan='2'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>联系人电话</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='169'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>　55510091</span></p></td></tr><tr style='HEIGHT: 20px'><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='149'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>停车费</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; WORD-BREAK: break-all; BORDER-TOP: #f0f0f0; BORDER-RIGHT: #f0f0f0; PADDING-TOP: 0px' width='161'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>无</span></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: windowtext 1px solid; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='65' colspan='2'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>其他情况说明</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='169'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>　</span></p></td></tr><tr style='HEIGHT: 26px'><td style='BORDER-BOTTOM: #f0f0f0; BORDER-LEFT: windowtext 1px solid; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' rowspan='2' width='68'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>评估信息</span></strong></p><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>　</span></strong></p></td><td style='BORDER-BOTTOM: #f0f0f0; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='149'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>评估机构名称</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; WORD-BREAK: break-all; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='161'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>上海大宏资产评估有限公司</span></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='65' colspan='2'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>评估结果</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='169'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>完成</span></p></td></tr><tr style='HEIGHT: 35px'><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: windowtext 1px solid; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='149'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>评估价格</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; WORD-BREAK: break-all; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='161'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>18400</span><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>元</span></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='65' colspan='2'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>评估结果有效截止日期</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='169'></td></tr><tr style='HEIGHT: 19px'><td style='BORDER-BOTTOM: black 1px solid; BORDER-LEFT: windowtext 1px solid; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: windowtext 1px solid; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' rowspan='4' width='68'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>车辆取得方式</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='149'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>提车签署文件</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; WORD-BREAK: break-all; BORDER-TOP: #f0f0f0; BORDER-RIGHT: black 1px solid; PADDING-TOP: 0px' width='395' colspan='4'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>需签署《提车承诺书》</span></p></td></tr><tr style='HEIGHT: 36px'><td style='BORDER-BOTTOM: black 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' rowspan='2' width='149'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>提车缴费说明</span></strong></p></td><td style='BORDER-BOTTOM: #f0f0f0; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; WORD-BREAK: break-all; BORDER-TOP: #f0f0f0; BORDER-RIGHT: black 1px solid; PADDING-TOP: 0px' width='395' colspan='4'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='COLOR: #111111; FONT-SIZE: 18px'><span style='FONT-FAMILY: Calibri'>1</span></span><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>、买受人提车时自行与停车场物业进行停车费结算；</span></p></td></tr><tr style='HEIGHT: 72px'><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; WORD-BREAK: break-all; BORDER-TOP: #f0f0f0; BORDER-RIGHT: black 1px solid; PADDING-TOP: 0px' width='395' colspan='4'></td></tr><tr style='HEIGHT: 36px'><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='149'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>其他说明</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; WORD-BREAK: break-all; BORDER-TOP: #f0f0f0; BORDER-RIGHT: black 1px solid; PADDING-TOP: 0px' width='395' colspan='4'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>车辆按现状拍卖</span><span style='COLOR: #111111; FONT-SIZE: 18px'><span style='FONT-FAMILY: Calibri'>/</span></span><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>具体提车时间等法院通知交接</span></p></td></tr><tr style='HEIGHT: 44px'><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: windowtext 1px solid; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='68'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>拍卖成交后法院提供文件</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; WORD-BREAK: break-all; BORDER-TOP: #f0f0f0; BORDER-RIGHT: black 1px solid; PADDING-TOP: 0px' width='545' colspan='5'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>法院执行裁定书、协助执行通知书、法院执行判决书</span><span style='COLOR: #111111; FONT-SIZE: 18px'><span style='FONT-FAMILY: Calibri'>/</span></span><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>调解书、拍卖成交确认书</span></p></td></tr><tr style='HEIGHT: 53px'><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: windowtext 1px solid; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' rowspan='4' width='68'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>拍卖成交后买受人过户证件要求说明</span></strong></p></td><td style='BORDER-BOTTOM: #f0f0f0; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; WORD-BREAK: break-all; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='545' colspan='5'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='COLOR: #111111; FONT-SIZE: 18px'><span style='FONT-FAMILY: Calibri'>1</span></span><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>、</span><span style='FONT-SIZE: 9px'>  </span><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>沪籍车辆成交后，沪籍人提供有效身份证、户口簿、车辆额度证明单；非沪籍人除提供有效身份证、在沪居住证、车辆额度证明单。</span></p></td></tr><tr style='HEIGHT: 53px'><td style='BORDER-BOTTOM: #f0f0f0; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; WORD-BREAK: break-all; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='545' colspan='5'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='COLOR: #111111; FONT-SIZE: 18px'><span style='FONT-FAMILY: Calibri'>2</span></span><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>、</span><span style='FONT-SIZE: 9px'>  </span><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>非沪籍车辆成交后，由买受人自行了解当地办证政策，成交后不能过户转籍的风险由买受人自行承担。</span></p></td></tr><tr style='HEIGHT: 72px'><td style='BORDER-BOTTOM: #f0f0f0; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; WORD-BREAK: break-all; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='545' colspan='5'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='COLOR: #111111; FONT-SIZE: 18px'><span style='FONT-FAMILY: Calibri'>3</span></span><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>、</span><span style='FONT-SIZE: 9px'>  </span><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>买受人如需办理沪</span><span style='COLOR: #111111; FONT-SIZE: 18px'><span style='FONT-FAMILY: Calibri'>C</span></span><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>牌照，除提供有效身份证外，还需提供住址为上海市外环以外的本市户口簿或外环以外有效的居住证。</span></p></td></tr><tr style='HEIGHT: 19px'><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; WORD-BREAK: break-all; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='545' colspan='5'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>　</span></p></td></tr><tr style='HEIGHT: 70px'><td style='BORDER-BOTTOM: black 1px solid; BORDER-LEFT: windowtext 1px solid; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' rowspan='5' width='68'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>过户税费及相关费用承担说明</span></strong></p></td><td style='BORDER-BOTTOM: #f0f0f0; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; WORD-BREAK: break-all; BORDER-TOP: #f0f0f0; BORDER-RIGHT: black 1px solid; PADDING-TOP: 0px' width='545' colspan='5'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='COLOR: #111111; FONT-SIZE: 18px'><span style='FONT-FAMILY: Calibri'>1</span></span><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>、</span><span style='FONT-SIZE: 9px'>  </span><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>车辆成交后，在办理过户时所涉及的一切费用均由买受人承担（包括但不限于车辆退牌费、车辆上牌费、过户交易费、补证费、补验车、违章罚款等）。</span></p></td></tr><tr style='HEIGHT: 53px'><td style='BORDER-BOTTOM: #f0f0f0; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; WORD-BREAK: break-all; BORDER-TOP: #f0f0f0; BORDER-RIGHT: black 1px solid; PADDING-TOP: 0px' width='545' colspan='5'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='COLOR: #111111; FONT-SIZE: 18px'><span style='FONT-FAMILY: Calibri'>2</span></span><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>、</span><span style='FONT-SIZE: 9px'>  </span><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>沪籍车辆成交后，买受人应在本公司协助下，及时办理车辆过户手续。如买受人不及时配合，则须对自己的行为承担相应法律责任。</span></p></td></tr><tr style='HEIGHT: 89px'><td style='BORDER-BOTTOM: #f0f0f0; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; WORD-BREAK: break-all; BORDER-TOP: #f0f0f0; BORDER-RIGHT: black 1px solid; PADDING-TOP: 0px' width='545' colspan='5'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='COLOR: #111111; FONT-SIZE: 18px'><span style='FONT-FAMILY: Calibri'>3</span></span><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>、</span><span style='FONT-SIZE: 9px'>  </span><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>沪籍车辆：拍卖结束后，买受人应在法院规定时间内付清抵扣保证金后的剩余款项，因车辆尚未办理退牌手续，买受人应向辅助机构支付办证押金</span><span style='COLOR: #111111; FONT-SIZE: 18px'><span style='FONT-FAMILY: Calibri'>9</span></span><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>万元；（货车黄牌</span><span style='COLOR: #111111; FONT-SIZE: 18px'><span style='FONT-FAMILY: Calibri'>/</span></span><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>沪</span><span style='COLOR: #111111; FONT-SIZE: 18px'><span style='FONT-FAMILY: Calibri'>C</span></span><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>牌除外）。</span></p></td></tr><tr style='HEIGHT: 36px'><td style='BORDER-BOTTOM: #f0f0f0; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; WORD-BREAK: break-all; BORDER-TOP: #f0f0f0; BORDER-RIGHT: black 1px solid; PADDING-TOP: 0px' width='545' colspan='5'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='COLOR: #111111; FONT-SIZE: 18px'><span style='FONT-FAMILY: Calibri'>4</span></span><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>、</span><span style='FONT-SIZE: 9px'>  </span><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>非沪籍车辆：拍卖结束后，买受人应在法院规定时间内付清抵扣保证金后的剩余款项。</span></p></td></tr><tr style='HEIGHT: 19px'><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; WORD-BREAK: break-all; BORDER-TOP: #f0f0f0; BORDER-RIGHT: black 1px solid; PADDING-TOP: 0px' width='545' colspan='5'></td></tr><tr style='HEIGHT: 57px'><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: windowtext 1px solid; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='68'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>其他特别情况说明</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; WORD-BREAK: break-all; BORDER-TOP: #f0f0f0; BORDER-RIGHT: black 1px solid; PADDING-TOP: 0px' width='545' colspan='5'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='COLOR: #111111; FONT-SIZE: 18px'><span style='FONT-FAMILY: Calibri'>1</span></span><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>、</span><span style='FONT-SIZE: 9px'>  </span><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>该车不带牌拍卖。</span></p></td></tr><tr style='HEIGHT: 72px'><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: windowtext 1px solid; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; BORDER-TOP: #f0f0f0; BORDER-RIGHT: windowtext 1px solid; PADDING-TOP: 0px' width='68'><p style='TEXT-ALIGN: left'><strong><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>标的综合描述</span></strong></p></td><td style='BORDER-BOTTOM: windowtext 1px solid; BORDER-LEFT: #f0f0f0; PADDING-BOTTOM: 0px; PADDING-LEFT: 7px; PADDING-RIGHT: 7px; BACKGROUND: none transparent scroll repeat 0% 0%; WORD-BREAK: break-all; BORDER-TOP: #f0f0f0; BORDER-RIGHT: black 1px solid; PADDING-TOP: 0px' width='545' colspan='5'><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'> </span></p><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'>沪HJ9220北京现代牌小型轿车；品牌型号：BH7162MX；发动机号：9B174435；车架号：LBEXDAEB29X746132；使用性质：非营运；表显里程不详；年检有效期:2018年6月；启用日期:2009年6月；不带牌；不办转籍；无车辆登记证、有行驶证、无购置证、钥匙一把；违章：有（至少2个违章，罚款400元）；有查封；黑色；排量：1599ML 82KW；停车费：无；车辆停放地址：上海市静安区康定路1097号上海市静安区人民法院后面停车场。拍卖成交后，买受人凭法律文书办理车辆转移登记。在办理车辆转移登记时所涉及的一切费用均由买受人承担（包括但不限于车辆退牌费、车辆上牌费、过户交易费、补证费、补验车、违章罚款等）。车辆成交后，由买受人自行了解当地办证政策，成交后不能过户转籍的风险由买受人自行承担。</span></p><p style='TEXT-ALIGN: left; TEXT-INDENT: 36px'><span style='FONT-FAMILY: 宋体; COLOR: #111111; FONT-SIZE: 18px'> </span></p></td></tr><tr><td style='BORDER-BOTTOM: #f0f0f0; BORDER-LEFT: #f0f0f0; BACKGROUND-COLOR: transparent; BORDER-TOP: #f0f0f0; BORDER-RIGHT: #f0f0f0' width='69'></td><td style='BORDER-BOTTOM: #f0f0f0; BORDER-LEFT: #f0f0f0; BACKGROUND-COLOR: transparent; BORDER-TOP: #f0f0f0; BORDER-RIGHT: #f0f0f0' width='145'></td><td style='BORDER-BOTTOM: #f0f0f0; BORDER-LEFT: #f0f0f0; BACKGROUND-COLOR: transparent; WORD-BREAK: break-all; BORDER-TOP: #f0f0f0; BORDER-RIGHT: #f0f0f0' width='167'></td><td style='BORDER-BOTTOM: #f0f0f0; BORDER-LEFT: #f0f0f0; BACKGROUND-COLOR: transparent; BORDER-TOP: #f0f0f0; BORDER-RIGHT: #f0f0f0' width='61'></td><td style='BORDER-BOTTOM: #f0f0f0; BORDER-LEFT: #f0f0f0; BACKGROUND-COLOR: transparent; BORDER-TOP: #f0f0f0; BORDER-RIGHT: #f0f0f0' width='3'></td><td style='BORDER-BOTTOM: #f0f0f0; BORDER-LEFT: #f0f0f0; BACKGROUND-COLOR: transparent; BORDER-TOP: #f0f0f0; BORDER-RIGHT: #f0f0f0' width='167'></td></tr></tbody></table><p><span style='FONT-FAMILY: Calibri'> </span></p><p> </p><p></p><br><a href='//img30.360buyimg.com/popWaterMark/jfs/t1/59676/32/4022/3082413/5d22dec5E6dda5151/9471aa795b9aa8c8.jpg' target='_blank'><img src ='//img30.360buyimg.com/popWaterMark/s1000x750_jfs/t1/59676/32/4022/3082413/5d22dec5E6dda5151/9471aa795b9aa8c8.jpg'/></a><br><br><a href='//img30.360buyimg.com/popWaterMark/jfs/t1/70863/2/4095/2751540/5d22dee0Eaa98bf46/a68770bb8f560aa1.jpg' target='_blank'><img src ='//img30.360buyimg.com/popWaterMark/s1000x750_jfs/t1/70863/2/4095/2751540/5d22dee0Eaa98bf46/a68770bb8f560aa1.jpg'/></a><br><br><a href='//img30.360buyimg.com/popWaterMark/jfs/t1/44839/16/4527/2487138/5d22dee9E6f699f5d/ff13c4001a3a757a.jpg' target='_blank'><img src ='//img30.360buyimg.com/popWaterMark/s1000x750_jfs/t1/44839/16/4527/2487138/5d22dee9E6f699f5d/ff13c4001a3a757a.jpg'/></a><br><br><a href='//img30.360buyimg.com/popWaterMark/jfs/t1/65215/2/3936/3675662/5d22deeaEce4e5fda/4fec7921f18ffac8.jpg' target='_blank'><img src ='//img30.360buyimg.com/popWaterMark/s1000x750_jfs/t1/65215/2/3936/3675662/5d22deeaEce4e5fda/4fec7921f18ffac8.jpg'/></a><br><br><a href='//img30.360buyimg.com/popWaterMark/jfs/t1/47194/23/4554/3058497/5d22deecEb3e701a8/9aa645fd64f46761.jpg' target='_blank'><img src ='//img30.360buyimg.com/popWaterMark/s1000x750_jfs/t1/47194/23/4554/3058497/5d22deecEb3e701a8/9aa645fd64f46761.jpg'/></a><br><br><a href='//img30.360buyimg.com/popWaterMark/jfs/t1/69109/8/4036/2457983/5d22deecE852d16d8/da1cbc196b3f2868.jpg' target='_blank'><img src ='//img30.360buyimg.com/popWaterMark/s1000x750_jfs/t1/69109/8/4036/2457983/5d22deecE852d16d8/da1cbc196b3f2868.jpg'/></a><br><br><a href='//img30.360buyimg.com/popWaterMark/jfs/t1/69790/33/4033/2418269/5d22deecEd141f8b3/0243872bb1bd1972.jpg' target='_blank'><img src ='//img30.360buyimg.com/popWaterMark/s1000x750_jfs/t1/69790/33/4033/2418269/5d22deecEd141f8b3/0243872bb1bd1972.jpg'/></a><br><br><a href='//img30.360buyimg.com/popWaterMark/jfs/t1/53616/36/4437/2912786/5d22deecE14b5a545/4338e77e45326472.jpg' target='_blank'><img src ='//img30.360buyimg.com/popWaterMark/s1000x750_jfs/t1/53616/36/4437/2912786/5d22deecE14b5a545/4338e77e45326472.jpg'/></a><br>"
    table = table.replace("\\", "")
    # print(table)
    table_dict, table_list = extract_table_new(table)
    print(table_dict)
    print(table_list)
    print(get_field_info(table_dict, table_list))
    
    # print(filter_tags(table, "123"))

    # print(date_offset('2019-02-15', -15))
    # print(date_offset('2019-08-14', -62))
    # forward_interval = 62
    # forward_interval = 60
    # backwards_interval = 0
    # interval = 15
    # start_date = time.strftime('%Y-%m-%d')
    # # start_date = '2013-07-01'
    # # offset_date = date_offset(start_date, 0 - forward_interval)
    # offset_date = date_offset(start_date, forward_interval)
    # print(offset_date)


