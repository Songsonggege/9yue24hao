# -*- coding: utf-8 -*-
#__author__: wangke
#__date__: 2019/7/25  15:36
#__ide__: PyCharm
import hashlib
import re


def get_id(text):
    """
    文书号去除特殊字符再md5
    :param text:
    :return :
    """
    text = re.sub("[^a-zA-Z0-9\\u4e00-\\u9fa5]", "", text)
    m = hashlib.md5()
    m.update(text.encode("utf8"))
    return m.hexdigest()