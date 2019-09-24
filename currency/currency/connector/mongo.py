# author:胡已源
# datetime:2019/9/4 上午10:05
# software: PyCharm


import pymongo
# from ..settings import MONGO_ADDR, MONGO_AUTH, MONGO_REPLICASET, MONGODB_DB_NAME

from scrapy.utils.project import get_project_settings

settings = get_project_settings()
MONGO_ADDR = settings['MONGO_ADDR']
MONGO_AUTH = settings['MONGO_AUTH']
MONGO_REPLICASET = settings['MONGO_REPLICASET']
MONGODB_DB_NAME = settings['MONGODB_DB_NAME']


def get_mongo_connection():
    client = pymongo.MongoClient(MONGO_ADDR, replicaSet=MONGO_REPLICASET)
    if MONGO_AUTH is not None:
        client[MONGODB_DB_NAME].authenticate(**MONGO_AUTH)

    db = client[MONGODB_DB_NAME]
    return db, client

# db = get_mongo_connection()
#
# for i in db['cc101'].find():
#     print(i)
