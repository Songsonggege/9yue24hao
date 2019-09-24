# -*- coding: utf-8 -*-
from pm import settings
import pymongo
import traceback
import requests
import json
# import time
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class PmPipeline(object):
    def __init__(self):
        host = settings.MONGODB_HOST
        port = settings.MONGODB_PORT
        dbname = settings.MONGODB_DBNAME
        self.client = pymongo.MongoClient(host=host, port=port)
        self.db = self.client[dbname]
        self.spider_name = ''

    def process_item(self, item, spider):
        # print(1111111111)
        data_info = dict(item)
        print(data_info)

        # if not self.spider_name:
        #     self.spider_name = spider.name + time.strftime('_%Y%m%d_%H%M%S')
        # try:
        #     self.db[self.spider_name].insert_one(data_info)
        # except:
        #     spider.logger.error('pipeline error: ' + str(data_info) + ' ' + traceback.format_exc())
        return item

    def close_spider(self, spider):
        self.client.close()


class UploadPipeline(object):
    def __init__(self):
        self.session = requests.session()
        header = {
            'Content-Type': 'application/json'
        }
        url = 'http://beehive.fybdp.com/login'
        data = {"userName": "songzhengyang", "passWord": "1993426"}
        # resp = requests.post(url, headers=header, data=json.dumps(data))
        resp = self.session.post(url, headers=header, data=json.dumps(data))
        self.auth = resp.headers['Authorization']

    def db_administ(self, item, crawlerName, datasetId):
        num = 10
        while num > 0:
            try:
                data = []
                temp = {}
                temp['datasetId'] = datasetId  # '54ffd76205f34d33b5076d4b7b66f4eb' 分类的处罚
                if 'source_url' in item.keys():
                    temp['url'] = item['source_url']
                else:
                    temp['url'] = item['url']
                temp['data'] = json.dumps(item, ensure_ascii=False)

                temp['crawlerTypeTag'] = 'pythonCrawler'

                temp['filter'] = True
                temp['crawlerName'] = crawlerName
                temp['userName'] = '宋争洋'
                data.append(temp)

                url = 'http://beehive.fybdp.com/tasks/submit/profitbatch/'

                user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'

                headers = {'User-Agent': user_agent,
                           'Content-Type': 'application/json',
                           'Authorization': self.auth
                           }

                # resp = requests.post(url, data=json.dumps(data), headers=headers, timeout=40)
                resp = self.session.post(url, data=json.dumps(data), headers=headers, timeout=40)
                # print(resp.json())

                # resp = json.loads(resp)
                res = resp.json()
                if '成功' in res.get('msg', ''):
                    print('上传成功')
                    return True
                else:
                    print('上传未成功 继续上传')
                    continue

            except:
                print(traceback.format_exc())

    def process_item(self, item, spider):  # 处理items
        ''' 写处理语句，比如保存等'''

        # set_id_ad = '54ffd76205f34d33b5076d4b7b66f4eb'  # 分类的处罚
        # set_id_adp = '44fad84a38ea40bba2b63728cba7dae2'  # 不分类处罚
        # set_id_prep = 'c4c5c5dc77ce45a19a9aa4368314b580'  # 许可不分类
        # set_id_prepp = 'a10d61f3e8184c679f04f544bb9766bd' #许可分类
        # set_id_preppp = '175a1f37525f4d3ca3b2aa3abff794e5'
        set_id_preppp = '9cc21fe7a70848ad8086fb8f436c0676'
        item = dict(item)
        # print(item)

        if spider.name == 'sf_caa123':
            self.db_administ(item, '司法拍卖-中国拍卖行业协会', set_id_preppp)

        if spider.name == 'sf_taobao':
            self.db_administ(item, '司法拍卖-阿里拍卖', set_id_preppp)

        # if spider.name == 'CFXK-ZYZ-0412-003':
        #     self.db_administ(item, '河南省新乡市行政许可',set_id_prepp)

        return item  #
