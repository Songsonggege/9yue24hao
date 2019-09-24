# -*- coding: utf-8 -*-
# __author__: wangke
# __date__: 2019/8/7  11:54
# __ide__: PyCharm
from datetime import datetime, timedelta


def time_offset(time):
    d = datetime.strptime(time, '%Y-%m-%d')
    d1 = d + timedelta(days=29)
    return (str(d1).split(" ")[0])
