# author:胡已源
# datetime:2019/9/6 下午4:16
# software: PyCharm

import json
import requests
import threading
import traceback
from typing import TypeVar, List
from functools import wraps

T = TypeVar('T', List[dict], dict)  # Must be List or dict


class LackParameters(Exception):
    def __init__(self, E):
        self.errorMessage = E


class Decorator(object):
    # 创建一个线程锁,这是一个类变量，类似于Java中静态变量
    __lock = threading.Lock()
    __instance = None

    # 定义一个高阶函数，cls参数是一个类
    # 同时它是一个静态方法，类似于Java中静态(类)方法
    @staticmethod
    def singleton(cls):
        # 定义一个私有方法,wraps作用不知道的自己查,不感兴趣的也不用知道
        @wraps(cls)
        def __wrapper(*args, **kw):
            # 如果类变量__instance不存在就新建，存在就返回
            if Decorator.__instance is None:
                # 在执行with块代码的时候加上线程锁，执行完毕释放线程锁
                # 此线程锁不是GIL锁
                with Decorator.__lock:
                    # 如果类变量__instance不存在就新建，存在就返回
                    if Decorator.__instance is None:
                        # 新建一个类
                        Decorator.__instance = cls(*args, **kw)
                    return Decorator.__instance
            return Decorator.__instance

        # 返回值为函数叫做闭包
        return __wrapper


# singleton函数是一个装饰器，它接受一个类或函数作为变量，并返回一个函数
# 创建类:DecoratorSingleton()相当于执行了singleton(CrawlerInterFace())
# lock是一个线程锁
@Decorator.singleton
class CrawlerInterFace(object):
    """ 爬虫数据提交接口类 """

    _max_retry: int = 10

    def __init__(self, user_name, pass_word):
        self.session = requests.session()
        self.session.keep_alive = False
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
        }
        self.target_url = "http://beehive.fybdp.com/tasks/submit/profitbatch/"
        self.user_name = ""
        self.auth = self.login(user_name, pass_word)

    def login(self, user_name: str, pass_word: str) -> str:
        """
        登录爬虫平台获取 Authorization
        :param user_name:用户名
        :param pass_word:密码
        :return:返回验证信息
        """
        url = "https://beehive.fybdp.com/login"
        r = self.session.post(
            url,
            headers=self.headers,
            data=json.dumps({"userName": user_name, "passWord": pass_word})
        )
        self.user_name = r.json()['head']['Name']
        auth = r.headers['Authorization']
        return auth

    def check_data(self, kwargs: dict) -> List[dict]:
        del kwargs['self']
        for k, v in kwargs.items():
            if isinstance(v, str):
                if not bool(v and v.strip()):
                    raise LackParameters("%s参数为空或者None" % k)

        data = []
        if isinstance(kwargs.get("item_data"), dict):
            data.append(kwargs.get("item_data"))
        else:
            data = kwargs.get("item_data")

        for item in data:
            item['data'] = json.dumps(item.copy(), ensure_ascii=False)
            item['datasetId'] = kwargs.get("dataset_Id")
            item['crawlerTypeTag'] = 'pythonCrawler'
            item['filter'] = kwargs.get("filter_")
            item['crawlerName'] = kwargs.get("crawler_name")
            item['userName'] = self.user_name

            if item.get('source_url'):
                item['url'] = item['source_url']
            elif item.get('url'):
                item['url'] = item['url']
            else:
                raise LackParameters("item数据中缺少source_url")

        return data

    def submit_data(self, item_data: T, crawler_name: str, dataset_Id: str, filter_: bool = True):
        """
        数据提交
        :param item_data: 需要上传的数据,可以是字典或者列表
        :param crawler_name: 爬虫的名称
        :param dataset_Id:数据集Id
        :param filter_: 是否开始数据过滤
        :return: 成功或失败
        """
        for _ in range(self._max_retry):
            try:
                kwargs = locals()
                data = self.check_data(kwargs)
                self.headers['Authorization'] = self.auth
                r = self.session.post(self.target_url, data=json.dumps(data), headers=self.headers, timeout=60)
                msg = r.json()
                if '成功' in msg['msg']:
                    print(msg)
                    break
                else:
                    print("上传失败")
                    print(msg)

            except Exception as e:
                print(e)
                print(traceback.format_exc())


if __name__ == '__main__':
    # 创建一个任务函数
    def task():
        # 获取DecoratorSingleton类实例/对象
        crawler = CrawlerInterFace("huyiyuan", "123456")
        print("验证请求：", crawler.auth)
        print("类Id：", id(crawler))
        print(crawler.user_name)


    # 循环创建多个线程
    for i in range(10):
        t = threading.Thread(target=task)
        t.start()
