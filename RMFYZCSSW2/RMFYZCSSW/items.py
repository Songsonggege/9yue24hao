# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class RmfyzcsswItem(scrapy.Item):
    # define the fields for your item here like:
    # 主键
    uid = scrapy.Field()
    # # 主键
    # _id = scrapy.Field()
    # 源网址
    url = scrapy.Field()
    # 竞买公告
    announcement = scrapy.Field()
    # 起拍价
    starting_price = scrapy.Field()
    # 处置单位
    disposalunit = scrapy.Field()
    # 竞拍结束时间
    end_date = scrapy.Field()
    # 评估价
    evaluationprice = scrapy.Field()
    # 标的物详情
    introduction = scrapy.Field()
    # 附件下载
    file = scrapy.Field()
    # 标的物所在地
    location = scrapy.Field()
    # 标题
    name = scrapy.Field()
    # 标的物所有人
    relation = scrapy.Field()
    # 竞拍开始时间
    start_date = scrapy.Field()
    # 标的物类型
    type = scrapy.Field()
    # 当前价
    current_price = scrapy.Field()
    # 拍品状态
    sales_status = scrapy.Field()
    # 拍卖阶段
    auction_phase = scrapy.Field()
    # 加价幅度
    mark_up = scrapy.Field()
    # 保证金
    deposits = scrapy.Field()
    # 保留价
    reserve_price = scrapy.Field()
    # 延时周期
    delay_period = scrapy.Field()
    # 竞买须知
    bidding_instructions = scrapy.Field()
    # 保证金须知
    margin_notes = scrapy.Field()
    # 出价记录
    bidding_record = scrapy.Field()
    # 优先购买权人
    preemptor = scrapy.Field()
    # 图片
    images = scrapy.Field()
    # 变卖预缴款
    sale_advance_payment = scrapy.Field()
    # 竞拍方式类型
    auction_type = scrapy.Field()
    # 处置依据
    disposal_basis = scrapy.Field()
    # 权证情况
    authority_card = scrapy.Field()
    # 拍品现状
    sales_actuality = scrapy.Field()
    # 权利限制情况
    restriction_of_rights = scrapy.Field()
    # 成交后提供的文件
    clinch_deal_file = scrapy.Field()
    # 拍品介绍
    lots_introduce = scrapy.Field()
    # 视频url地址
    videos = scrapy.Field()
    # 公告日期
    publish_date = scrapy.Field()
















