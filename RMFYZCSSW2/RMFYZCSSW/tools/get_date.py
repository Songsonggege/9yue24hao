# -*- coding: utf-8 -*-
#__author__: wangke
#__date__: 2019/7/26  18:04
#__ide__: PyCharm
import datetime
import re


def get_date(text):
    rul = re.search(r"\d{4}年\d+月\d+日", text).group()
    date = datetime.datetime.strptime(rul, '%Y年%m月%d日')
    return str(date)[:10]
