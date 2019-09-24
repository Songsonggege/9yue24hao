# author:胡已源
# datetime:2019/8/21 下午8:21
# software: PyCharm
# -*- coding: utf-8 -*-

import inspect
from currency.currency import settings


class PythonToMap(object):
    """将settings中的配置文件转换为字典"""

    @staticmethod
    def genMap(targetPy):
        targetObj = {}
        for key, obj in inspect.getmembers(targetPy):
            if inspect.isclass(obj):
                continue
            if inspect.ismodule(obj):
                continue
            if '__' in key:
                continue
            if inspect.ismethod(key):
                continue
            targetObj[key] = obj
        return targetObj


if __name__ == '__main__':
    print(PythonToMap.genMap(settings))
