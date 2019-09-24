# author:胡已源
# datetime:2019/9/5 上午11:52
# software: PyCharm


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


def is_empty(s: str) -> bool:
    return not bool(s and s.strip())


if __name__ == '__main__':
    pass
