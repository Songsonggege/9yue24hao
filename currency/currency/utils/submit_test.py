# author:胡已源
# datetime:2019/9/9 下午5:09
# software: PyCharm
from currency.currency.utils.mongo_utils import mongo_conn

from currency.currency.utils.crawler_InterFace_utils import CrawlerInterFace

database_name = "beehive"
col_name = "cc101"
collection = mongo_conn(database_name=database_name, col_name=col_name)

crawler = CrawlerInterFace("huyiyuan", "123456")
# 行政处罚分类
administrative = "54ffd76205f34d33b5076d4b7b66f4eb"

data = list()
for temp in collection.find():
    del temp['_id']
    data.append(temp)

for index in range((len(data) // 1000) + 1):
    data_list = data[index * 1000:(index + 1) * 1000]

    if not data_list:
        continue

    crawler.submit_data(data_list, "上海市城市管理行政执法局-行政处罚", administrative)
