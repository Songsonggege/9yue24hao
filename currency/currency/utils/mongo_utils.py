import pymongo


def mongo_conn(user_name=None, password=None, host="localhost:27017", database_name=None, is_settings=True,
               col_name=None):
    if user_name and password and database_name:
        mongo_uri = "mongodb://" + user_name + ":" + password + "@" + host + "/" + database_name
    elif is_settings:
        mongo_uri = "mongodb://" + host + "/" + database_name
    else:
        mongo_uri = "mongodb://" + host
    with pymongo.MongoClient(mongo_uri) as mongo_client:
        mongo_db = mongo_client[database_name]
        return mongo_db[col_name]


def mongo_beehive_conn(col_name):
    mongo_uri = "mongodb://view:view@172.16.40.1:27701,172.16.40.2:27701,172.16.40.3:27701/beehive"
    with pymongo.MongoClient(mongo_uri) as mongo_client:
        mongo_db = mongo_client['beehive']
        return mongo_db[col_name]


