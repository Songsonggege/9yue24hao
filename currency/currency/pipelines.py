# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
import pymongo
import json
import traceback
import requests

from .connector import mongo
from scrapy.exceptions import DropItem
from scrapy.utils.project import get_project_settings
from .utils import crawler_InterFace_utils


class BaseMongoPipeline(object):
    """ 本地Mongo管道 """

    def __init__(self):
        self.mongo_db = None
        self.mongo_client = None
        self.col_name = None

    # 开启爬虫时执行，只执行一次
    def open_spider(self, spider):
        self.mongo_db, self.mongo_client = mongo.get_mongo_connection()
        self.col_name = os.environ.get('CRAWLAB_COLLECTION')  # 集合名称，通过环境变量 CRAWLAB_COLLECTION 传过来

    def process_item(self, item, spider):
        if not item.get("_id"):
            raise DropItem("Missing _id in %s" % item)

        task_id = os.environ.get('CRAWLAB_TASK_ID')  # 将 task_id 设置为环境变量传过来的任务 ID
        if task_id:
            item['task_id'] = task_id

        # 如果 CRAWLAB_COLLECTION 不存在，则默认集合名称为 test
        if self.col_name:
            col_name = self.col_name
        else:
            col_name = item['mongo_collection']

        collection = self.mongo_db[col_name]
        mongo_update_instruction = item.get("mongo_update_instruction", None)

        if mongo_update_instruction is not None:
            collection.update_one(**mongo_update_instruction)
        else:
            raise Exception
        del item['mongo_update_instruction']
        del item['mongo_collection']
        return item

    def close_spider(self, spider):
        self.mongo_client.close()


class SubmitDataPipeline(object):
    """ 数据提交管道 """

    # 行政处罚分类
    administrative = "54ffd76205f34d33b5076d4b7b66f4eb"

    def __init__(self):
        self.crawler = crawler_InterFace_utils.CrawlerInterFace("huyiyuan", "12346")
        self.data_list = []
        self.valve = 1000  # 阀值,一次性提交的数据量

    def process_item(self, item, spider):  # 处理items
        """ 写处理语句，比如保存等 """

        self.data_list.append(item)
        if len(self.data_list) == self.valve:
            if spider.name == 'CFXK-5-240':
                self.crawler.submit_data(dict(item), "上海市城市管理行政执法局-行政处罚", "胡已圆", self.administrative)
        else:
            pass

        return item
