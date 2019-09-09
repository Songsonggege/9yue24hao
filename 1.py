import json
import csv
import requests
import pandas as pd
headers = {
    'sec-fetch-mode': 'cors',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,und;q=0.6',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
    'accept': 'application/json, text/plain, */*',
    'referer': 'https://marketingplatform.google.com/about/partners/find-a-partner',
    'authority': 'marketingplatform.google.com',
    'cookie': '1P_JAR=2019-8-22-3; ANID=AHWqTUlu-6FhD6f0NfXIc_zCBVkW3b9RzfYNhG9ilGhKEbCHIc_SztKDvqPVLlxz; NID=188=Qt-z-JsglXo0isBJLVH3ZM3b6GV_H2aFq6VlWwIV4SWeK-Ln5vB2trDO2V44hba_8fuxeZ8Zt9dJdkBLTxIrj0CiLg9LSvQvIFqFb9D_blQwaOf1bOo0YzCcMvj5W7DNPLxzGcYoMN0ztOvJOKXlD2t4-jm-_bIdcyoYGd6cbe0',
    'sec-fetch-site': 'same-origin',
    'x-client-data': 'CI62yQEIpbbJAQjBtskBCKmdygEIqKPKAQjiqMoBCJetygEIza3KAQjKr8oB',
}

# params = (
#     ('page', '1'),
#     ('geo', ''),
#     ('q', ''),
# )
values = []
for i in range(1, 51, 1):
    ue = "https://marketingplatform.google.com/about/partners/services/partner_search?&page={}&geo=&q=".format(i)
    response = requests.get(ue, headers=headers)
    dict_type = {0:'Sales Partner',1:'Certified Company'}
    dict_1 = {'300': 'Analytics', '310': 'Tag Manager', '390': 'Sales Partner', '320': 'Optimize', '330': 'Data Studio', '340': 'Attribution', '400': 'Display & Video 360', '410': 'Campaign Manager', '420': 'Search Ads 360', '430': 'Creative', '440': 'Surveys'}

    _json = json.loads(response.text)
    try:
        for item in _json[0]:
            data = {}
            data['name'] = item[13]
            data['address'] = item[15]
            data['partner_type'] = dict_type.get(item[16])
            certifications = item[10]
            if certifications:
                data['Product_certifications'] = [dict_1.get(x) for x in certifications]
            print(data)
            values.append(data)


    except:pass
header = ["name", "address", "partner_type", "Product_certifications"]
with open("wg.csv", 'a', encoding='utf-8', newline="") as fp:
    writer = csv.DictWriter(fp, header)  # 获取文件“写笔”，注意参数还需传递记录标题以映射，注意此时并不会真正写入标题
    writer.writeheader()  # 写入记录标题
    writer.writerows(values)


print("autuor:Songsong")
