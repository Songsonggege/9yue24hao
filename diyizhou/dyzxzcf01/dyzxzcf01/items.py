# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class CfxkItem(scrapy.Item):
    # define the fields for your item here like:
    adid = scrapy.Field()           #主键 1.编号、2.索引号、3.url、4.内容
    identifier = scrapy.Field()        #编号/编码/
    indexesCode = scrapy.Field()       #索引号
    prLegalPerson= scrapy.Field()  #法人代表
    name = scrapy.Field()   #标题(案件名称)名称，如果是表格统一标题并且表格内没标题的话：那么从内容中挑选能体现出这条数据特性的文本当做标题
    createdAt = scrapy.Field()   #发布日期
    prPunishmentAt = scrapy.Field()  #处罚日期
    type = scrapy.Field()      #哪一方面的处罚
    paragraph = scrapy.Field()   #段落<提取内容（保存<p>标签和<br>）>
    publisher = scrapy.Field()    #发布方(处罚方)
    images = scrapy.Field()       #图片地址
    regionCode = scrapy.Field()    #地区编号
    prPrincipal = scrapy.Field()   #被处罚主体pip
    prCause = scrapy.Field()      #处罚事由
    prGist = scrapy.Field()       #处罚依据
    prTarget = scrapy.Field()      #处罚结果
    categories= scrapy.Field()     #处罚类别(如：罚款、停业整顿等)p
    prCreditCode = scrapy.Field()   #代码(公司填同一信用代码、个人身份证)
    url = scrapy.Field()            #url地址
    prPhone = scrapy.Field()        #联系电话
    prAddress = scrapy.Field()    #被处罚主体地址
    fileType = scrapy.Field()     #文件类型(下载的文件是pdf picture excel doc 等)
    idMethod = scrapy.Field()     #表明是用文号、url或文本内容来hash生成主键的标记。是生成id的工具类内部生成的。
    uri = scrapy.Field()            #统一资源标识符(存入的哪个地方的一个地址)
    source_url = scrapy.Field()
    dispose = scrapy.Field()       #是否已解析Document




class FileDownloadItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    file_urls=scrapy.Field()
    files=scrapy.Field()