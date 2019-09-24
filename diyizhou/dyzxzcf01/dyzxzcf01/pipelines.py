# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
# import json
from scrapy.conf import  settings
import pymongo


class Dyzxzcf01Pipeline(object):
    # def __init__(self):
        #打开文件
        # self.f = open('cbrc.json','a',encoding='utf8')
    def __init__(self):
        # 获取setting主机名、端口号和数据库名称
        host = settings['MONGODB_HOST']
        port = settings['MONGODB_PORT']
        dbname = settings['MONGODB_DBNAME']

        # 创建数据库连接
        client = pymongo.MongoClient(host=host, port=port)

        # 指向指定数据库
        mdb = client['cbrc']

        # 获取数据库里面存放数据的表名
        self.post = mdb[settings['MONGODB_DOCNAME']]



    def process_item(self, item, spider):
        #用来存储数据
        #
        # json_item = json.dumps(dict(item), ensure_ascii=False)
        # self.f.write(json_item + '\n')
        data = dict(item)
        #指定向表中添加数据
        self.post.insert(data)
        return item

    def open_spider(self,spider):
        #启动爬虫时候调用
        print('{}爬虫启动了'.format(spider.name))
        pass

    def close_spider(self, spider):
        # 爬虫结束时候调用
        print('{}爬虫运行结束了'.format(spider.name))
        # self.f.close()
        pass
