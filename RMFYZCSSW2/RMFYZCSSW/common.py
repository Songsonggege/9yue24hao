import hashlib
import re

from lxml import etree
from w3lib import html

from urllib.parse import urljoin


def get_info_from_dict(table_dict, keywords):
    # keywords 是 ['所有人', '产权人为', '所有权人']
    # print('|'.join(keywords))
    for k, v in table_dict.items():
        if re.search('|'.join(keywords), k):
            return v.strip()
    return ''

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


def extract_table_new(html_str):
    result_list = []
    result_dict = {}
    # delete_index_list = []
    # simple_tr_list = []
    if html_str:
        html_tree = etree.HTML(html_str)
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
                key = td_str_list[0].replace('<p>', '').replace('</p>', '')
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
                        # result_list.append('<p>{}</p >'.format(key))
                        # result_list.append('<p>{}</p >'.format(value))
                        result_list.append(key)
                        result_list.append(value)
                        break
    return result_dict, result_list
def get_table_info(table_dict, table_list):
    item_dict = {}
    if table_dict:
        relation = get_info_from_dict(table_dict, ['所有人', '产权人为', '所有权人']).replace('<p>', '').replace('</p>', '').replace('<p/>', '')
        item_dict['relation'] = [relation] if relation else []
        item_dict['disposal_basis'] = get_info_from_dict(table_dict, ['权利来源', '处置依据', '拍卖依据']).replace('<p>',
                                                                                                            '').replace(
            '</p>', '')
        item_dict['authority_card'] = get_info_from_dict(table_dict, ['权证情况']).replace('<p>', '').replace('</p>',
                                                                                                               '')
        item_dict['sales_actuality'] = get_info_from_dict(table_dict, ['现状'])
        # item_dict['sales_actuality'] = '<p>{}</p>'.format(sales_actuality) if sales_actuality else ''
        item_dict['restriction_of_rights'] = get_info_from_dict(table_dict, ['权利限制'])
        # item_dict['restriction_of_rights'] = '<p>{}</p>'.format(restriction_of_rights) if restriction_of_rights else ''
        item_dict['clinch_deal_file'] = get_info_from_dict(table_dict, ['提供的文件'])
        # item_dict['clinch_deal_file'] = '<p>{}</p>'.format(clinch_deal_file) if clinch_deal_file else ''

        # lots_introduce = get_info_from_dict(table_dict, ['标的物介绍', '拍品介绍', '标的情况', '标的物基本信息'])
        # item_dict['lots_introduce'] = '<p>{}</p>'.format(lots_introduce) if lots_introduce else ''
        item_dict['lots_introduce'] = ''
        for k, v in table_dict.items():
            if re.search('|'.join(['标的物介绍', '拍品介绍', '标的情况', '标的物基本信息']), k):
                if v.strip():
                    item_dict['lots_introduce'] = v.strip()
                else:
                    lots_introduce = ''
                    len_table_list = len(table_list)
                    for index, each_p in enumerate(table_list):
                        m = re.search('<p>.*?(标的物介绍|拍品介绍|标的情况|标的物基本信息).*?</p>', each_p)
                        if m:
                            m1 = re.search('<p>.*?(标的物介绍|拍品介绍|标的情况|标的物基本信息).*?</p>(<p>.*</p>)', each_p)
                            if m1:
                                lots_introduce = m1.group(2)
                            else:
                                if index >= len_table_list - 1:
                                    lots_introduce = ''
                                else:
                                    for a in table_list[index + 1:]:
                                        if a.strip():
                                            lots_introduce = a.strip()
                                            break
                            break
                    item_dict['lots_introduce'] = lots_introduce
                break
    return item_dict
