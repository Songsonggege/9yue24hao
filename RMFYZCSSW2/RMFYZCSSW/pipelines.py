# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import json
import traceback

import pymongo

import requests


class RmfyzcsswPipeline(object):
    def __init__(self):
        self.session = requests.Session()
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
                # if 'source_url' in item.keys():
                #     temp['url'] = item['source_url']
                # else:
                #     temp['url'] = item['url']
                temp['data'] = json.dumps(item, ensure_ascii=False)

                temp['crawlerTypeTag'] = 'pythonCrawler'
                temp['filter'] = True

                temp['crawlerName'] = crawlerName  # 爬虫名
                temp['userName'] = '宋争洋'
                data.append(temp)

                url = 'http://beehive.fybdp.com/tasks/submit/profitbatch/'

                user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'

                headers = {'User-Agent': user_agent,
                           'Content-Type': 'application/json',
                           'Authorization': self.auth
                           }

                resp = self.session.post(url, data=json.dumps(data), headers=headers, timeout=60)
                # print(resp.json())

                # resp = json.loads(resp)
                res = resp.json()
                if '成功' in res['msg']:
                    print('上传成功')
                    return True
                else:
                    print('上传未成功 继续上传')
                    continue

            except:
                print(traceback.format_exc())

    def process_item(self, item, spider):  # 处理items
        ''' 写处理语句，比如保存等'''

        id = '9cc21fe7a70848ad8086fb8f436c0676'

        item = dict(item)
        # print(item)
        if spider.name == 'sfpm':
            self.db_administ(item, '司法拍卖人民法院诉讼资产网', id)

        return item


