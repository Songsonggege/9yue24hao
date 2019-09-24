# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PmItem(scrapy.Item):
    # define the fields for your item here like:
    uid = scrapy.Field()  # 主键 str
    url = scrapy.Field()  # 源网址 str
    announcement = scrapy.Field()  # 竞买公告 array（列表）保留P标签，保留br标签
    starting_price = scrapy.Field()  # 起拍价 str
    disposalunit = scrapy.Field()  # 处置单位 str
    end_date = scrapy.Field()  # 竞拍结束时间 str
    evaluationprice = scrapy.Field()  # 评估价 str
    introduction = scrapy.Field()  # 标的物详情 str 保留P标签，保留br标签
    file = scrapy.Field()  # 附件下载 str  --需要下载并保留文件的url
    location = scrapy.Field()  # 标的物所在地 str
    name = scrapy.Field()  # 标题
    relation = scrapy.Field()  # 标的物所有人 array 元素是str
    start_date = scrapy.Field()  # 竞拍开始时间 str
    type = scrapy.Field()  # 标的物类型 str
    current_price = scrapy.Field()  # 当前价 str
    # 拍品状态 str 比如撤回，即将开始，正在拍卖等。当网页拍品状态为结束，成功，成交，撤回时，不用重复抓取，其他比如正在拍卖，即将开始等状态都需要重复抓取。直到状态显示为拍卖结束为止
    sales_status = scrapy.Field()
    auction_phase = scrapy.Field()  # 拍卖阶段 str
    mark_up = scrapy.Field()  # 加价幅度 str
    deposits = scrapy.Field()  # 保证金 str
    reserve_price = scrapy.Field()  # 保留价 str
    delay_period = scrapy.Field()  # 延时周期 str
    bidding_instructions = scrapy.Field()  # 竞买须知 array 保留P标签，保留br标签
    margin_notes = scrapy.Field()  # 保证金须知 array 保留P标签，保留br标签
    # 下面字段说明 列表保存，包含bidding_record（出价记录）offer_state（出价状态）price，bidder，time
    bidding_record = scrapy.Field()
    # 下面字段说明 列表保存，包含bpreemptor，serial_number，bidder，rank，remarks
    preemptor = scrapy.Field()
    images = scrapy.Field()  # 图片 array 说明存储一个拍卖品的所有图片url
    sale_advance_payment = scrapy.Field()  # 变卖预缴款 str
    auction_type = scrapy.Field()  # 竞拍方式类型 str
    
    disposal_basis = scrapy.Field()  # 处置依据或权利来源 处置拍卖品所有权的来源依据
    authority_card = scrapy.Field()  # 权证情况 拍卖品的各种所有权证书文件的情况
    sales_actuality = scrapy.Field()  # 拍品现状 保留P标签，保留br标签。拍卖品现阶段的各种附带说明情况
    restriction_of_rights = scrapy.Field()  # 权利限制情况 保留P标签，保留br标签。拍卖品的所有权被法院查封限制的情况
    clinch_deal_file = scrapy.Field()  # 成交后提供的文件 保留P标签，保留br标签。拍卖品被拍卖成功之后能提供的各种附带文件
    lots_introduce = scrapy.Field()  # 拍品介绍 保留P标签，保留br标签。拍卖品的各种参数规格，注意事项的介绍
    videos = scrapy.Field()  # 视频url地址
    publish_date = scrapy.Field()  # 公告日期 法院发布拍卖公告的日期


class SfpmItem(scrapy.Item):
    # define the fields for your item here like:
    uid = scrapy.Field()  # 主键 str
    url = scrapy.Field()  # 源网址 str
    announcement = scrapy.Field()  # 竞买公告 array（列表）保留P标签，保留br标签
    starting_price = scrapy.Field()  # 起拍价 str
    disposalunit = scrapy.Field()  # 处置单位 str
    end_date = scrapy.Field()  # 竞拍结束时间 str
    evaluationprice = scrapy.Field()  # 评估价 str
    introduction = scrapy.Field()  # 标的物详情 str 保留P标签，保留br标签
    file = scrapy.Field()  # 附件下载 str  --需要下载并保留文件的url
    location = scrapy.Field()  # 标的物所在地 str
    name = scrapy.Field()  # 标题
    relation = scrapy.Field()  # 标的物所有人 object包括relation 和name
    start_date = scrapy.Field()  # 竞拍开始时间 str
    type = scrapy.Field()  # 标的物类型 str
    current_price = scrapy.Field()  # 当前价 str
    # 拍品状态 str 比如撤回，即将开始，正在拍卖等。当网页拍品状态为结束，成功，成交，撤回时，不用重复抓取，其他比如正在拍卖，即将开始等状态都需要重复抓取。直到状态显示为拍卖结束为止
    sales_status = scrapy.Field()
    auction_phase = scrapy.Field()  # 拍卖阶段 str
    mark_up = scrapy.Field()  # 加价幅度 str
    deposits = scrapy.Field()  # 保证金 str
    reserve_price = scrapy.Field()  # 保留价 str
    delay_period = scrapy.Field()  # 延时周期 str
    bidding_instructions = scrapy.Field()  # 竞买须知 array 保留P标签，保留br标签
    margin_notes = scrapy.Field()  # 保证金须知 array 保留P标签，保留br标签
    # 下面字段说明 列表保存，包含bidding_record（出价记录）offer_state（出价状态）price，bidder，time
    bidding_record = scrapy.Field()
    # 下面字段说明 列表保存，包含bpreemptor，serial_number，bidder，rank，remarks
    preemptor = scrapy.Field()
    images = scrapy.Field()  # 图片 array 说明存储一个拍卖品的所有图片url
    sale_advance_payment = scrapy.Field()  # 变卖预缴款 str
    auction_type = scrapy.Field()  # 竞拍方式类型 str
