# -*- coding: utf-8 -*-
import scrapy
import time
import json
import traceback
from pm import common
import re
from scrapy import exceptions
from lxml import etree
# import html
from pm.sf_taobao_url import get_doing_url, get_todo_url, get_over_url, get_break_url, get_revocation_url


class SfTaobaoSpider(scrapy.Spider):
    name = 'sf_taobao'
    # allowed_domains = ['sf.taobao.com', 'sf-item.taobao.com', 'susong-item.taobao.com', 'osdsc.alicdn.com']
    allowed_domains = ['sf.taobao.com', 'sf-item.taobao.com', 'susong-item.taobao.com', 'alicdn.com']
    # https://sf.taobao.com/item_list.htm?auction_source=0&st_param=-1&auction_start_seg=-1&page=2
    # https://sf.taobao.com/item_list.htm?auction_source=0&st_param=-1&auction_start_seg=-1&page=6
    # https://sf.taobao.com/item_list.htm?&auction_source=0&sorder=1&st_param=-1&auction_start_seg=-1

    start_urls = ['https://sf.taobao.com/item_list.htm']
    # test
    # start_urls = [
    #     'https://sf.taobao.com/item_list.htm?auction_source=0&sorder=1&st_param=-1&auction_start_seg=0&auction_start_from=2019-09-25&auction_start_to=2019-09-25',
    #     'https://sf.taobao.com/item_list.htm?auction_source=0&sorder=0&st_param=-1&auction_start_seg=&auction_start_from=2019-06-18&auction_start_to=2019-06-18',
    #     'https://sf.taobao.com/item_list.htm?auction_source=0&sorder=4&st_param=-1&auction_start_seg=&auction_start_from=2018-10-09&auction_start_to=2018-10-09',
    #     'https://sf.taobao.com/item_list.htm?auction_source=0&sorder=5&st_param=-1&auction_start_seg=0&auction_start_from=2018-10-21&auction_start_to=2018-10-21',
    #     'https://sf.taobao.com/item_list.htm?auction_source=0&sorder=2&st_param=-1&auction_start_seg=&auction_start_from=2014-05-13&auction_start_to=2014-05-13',
    #     'https://sf.taobao.com/item_list.htm?auction_source=0&sorder=2&start_price=300000&end_price=300000&st_param=-1&auction_start_from=2019-03-01&auction_start_to=2019-03-31',
    # ]
    # total_page = 0
    records_page = 1

    def start_requests(self):
        now_date = time.strftime('%Y-%m-%d')

        for url in get_doing_url(now_date):
            yield scrapy.Request(url)

        for url in get_over_url(now_date):
            yield scrapy.Request(url)

        # 分开爬
        for url in get_todo_url(now_date):
            yield scrapy.Request(url)

        for url in get_break_url(now_date):
            yield scrapy.Request(url)

        for url in get_revocation_url(now_date):
            yield scrapy.Request(url)

    def parse(self, response):
        # print(response.url)
        # print(response.text)
        try:
            data_list = json.loads(response.xpath('//script[@id="sf-item-list-data"]/text()').extract_first(), encoding='utf-8').get('data', [])
            # for data in data_list[:1]:
            for data in data_list:
                detail_id = data.get('id')
                # detail_id = '575705362007'  # 598593650410 和 575705362007 表格解析有冲突
                # detail_id = '598593650410'  # 598593650410 和 575705362007 表格解析有冲突
                # detail_id = '600097882535'  # desc 中有 \\
                # detail_id = '36338240687'  # 有视频
                # detail_id = '576617152500'  # 有优先购买权
                # detail_id = '600122485687'  # 竞买公告中有多附件
                # detail_id = '599539265866'  # 另外发请求获得附件，表格格式不一样，解析有问题
                # detail_id = '16794301233'  # 多竞拍记录
                # detail_id = '523158388129'  # 没有标的物详情
                if detail_id:
                    url = 'https://sf-item.taobao.com/sf_item/{}.htm'.format(detail_id)
                    uid = common.get_id(url)
                    starting_price = str(data.get('initialPrice', '') or '')
                    if starting_price:
                        starting_price = re.sub('\.0', '', starting_price).strip() + '元'
                    start = int(data.get('start', 0))
                    end = int(data.get('end', 0))
                    if start >= end:
                        end_date = ''
                    else:
                        end_date = common.to_time_str(int(end / 1000)) if end else ''
                    evaluationprice = str(data.get('consultPrice', '') or '')
                    if evaluationprice:
                        evaluationprice = re.sub('\.0', '', evaluationprice).strip() + '元'
                    name = data.get('title', '') or ''
                    start_date = common.to_time_str(int(start / 1000)) if start else ''
                    current_price = str(data.get('currentPrice', '') or '')
                    if current_price:
                        current_price = re.sub('\.0', '', current_price).strip() + '元'
                    sales_status = common.taobao_sales_status_dict.get(data.get('status', ''), '其他')
                    if sales_status == '其他':
                        self.logger.error(response.url + ' sales_status ' + data.get('status', ''))
                    bidCount = int(data.get('bidCount', 0) or 0)
                    item_dict = {
                        'uid': uid,
                        'url': url,
                        # 'announcement': [],
                        'starting_price': starting_price,
                        # 'disposalunit': disposalunit,
                        'end_date': end_date,
                        'evaluationprice': evaluationprice,
                        # 'introduction': [],
                        # 'file': [],
                        # 'location': '',
                        'name': name,
                        'relation': [],  # todo 在表格里面找
                        'start_date': start_date,
                        'type': '',  # todo 有，但是没有找到
                        'current_price': current_price,
                        'sales_status': sales_status,
                        'auction_phase': '',
                        # 'mark_up': mark_up,
                        # 'deposits': deposits,
                        'reserve_price': '',  # 无
                        # 'delay_period': delay_period,
                        # 'bidding_instructions': bidding_instructions,
                        'margin_notes': [],  # 无
                        'bidding_record': [],
                        'preemptor': [],  # 无
                        # 'images': [],
                        # 'sale_advance_payment': sale_advance_payment,
                        # 'auction_type': auction_type,

                        'disposal_basis': '',  # todo 在表格里面找
                        'authority_card': '',  # todo 在表格里面找
                        'sales_actuality': '',  # todo 在表格里面找
                        'restriction_of_rights': '',  # todo 在表格里面找
                        'clinch_deal_file': '',  # todo 在表格里面找
                        'lots_introduce': '',  # todo 在表格里面找
                        # 'videos': '',
                        # 'publish_date': '',  # 在竞买公告里面
                    }

                    yield scrapy.Request(url, callback=self.get_detail, meta={'detail_id': str(detail_id), 'bidCount': bidCount, 'item_dict': item_dict})

            # 翻页
            next_page = response.xpath('//a[@class="next"]/@href').extract_first()
            if next_page:
                next_page = 'https:' + next_page.strip() if 'https:' not in next_page else next_page.strip()
                yield scrapy.Request(next_page)

        except:
            self.logger.error(response.url + ' 列表页出错 ' + traceback.format_exc())
            # print('11111111111111' + traceback.format_exc())

    def get_detail(self, response):
        # print(response.url)
        # print(response.text)
        detail_id = response.meta['detail_id']
        item_dict = response.meta['item_dict']
        bidCount = response.meta['bidCount']
        # response.xpath('//span[contains(text(), "变卖预缴款")]/following-sibling::span[1]//text()').extract()
        delay_period = self.extrac_info(response, '延时周期')
        mark_up = self.extrac_info(response, '加价幅度')
        if mark_up:
            mark_up = re.sub('\.0', '', mark_up).strip() + '元'
        sale_advance_payment = self.extrac_info(response, '变卖预缴款')
        if sale_advance_payment:
            sale_advance_payment = re.sub('\.0', '', sale_advance_payment).strip() + '元'
        auction_type = self.extrac_info(response, '类 型')
        disposalunit = self.extrac_info(response, '处置单位')
        deposits = self.extrac_info(response, '保 证 金')
        if deposits:
            deposits = re.sub('\.0', '', deposits).strip() + '元'
        location = response.xpath('//div[@class="detail-common-text item-address"]//text()').extract()
        location = ''.join(location).strip() if location else ''
        h1 = response.xpath('//h1//text()').extract()
        if h1:
            h1 = ''.join(h1)
            m = re.search('【(.*?)】', h1)
            auction_phase = m.group(1) if m else ''
        else:
            auction_phase = ''

        announcement_url = response.xpath('//div[@id="J_NoticeDetail"]/@data-from').extract_first()  # 公告中可能有附件  600122485687 中有附件
        bidding_instructions_url = response.xpath('//div[@id="J_ItemNotice"]/@data-from').extract_first()
        introduction_url = response.xpath('//div[@id="J_desc"]/@data-from').extract_first()  # 可能没有这个标签，即没有 标的物详情
        bidding_record_url = response.xpath('//div[@id="J_RecordContent"]/@data-from').extract_first()
        file_url = response.xpath('//div[@id="J_DownLoadFirst"]/@data-from').extract_first()  # 可能有附件
        if not file_url:
            file_url = response.xpath('//p[@id="J_DownLoadFirst"]/@data-from').extract_first()
        file_url = 'http:' + file_url if file_url else ''
        # file_url = 'http://sf-item.taobao.com/json/get_gov_attach.htm?id=599539265866'
        videos = response.xpath('//div[@id="player"]/@data-src').extract_first()
        videos = 'http:' + videos if videos else ''

        img_list = response.xpath('//div[@class="sf-pic-slide clearfix"]//img/@data-ks-lazyload').extract() or []
        img_list = ['http:' + i for i in img_list if img_list]

        # if not announcement_url or not bidding_instructions_url or not introduction_url or not bidding_record_url:
        if not announcement_url or not bidding_instructions_url or not bidding_record_url:
            self.logger.error(detail_id + ' 出错，少了一些url，请检查')
            raise exceptions.DropItem

        announcement_url = 'http:' + announcement_url if announcement_url[:4] != 'http' else announcement_url
        bidding_instructions_url = 'http:' + bidding_instructions_url if bidding_instructions_url[:4] != 'http' else bidding_instructions_url
        introduction_url = 'http:' + introduction_url if introduction_url[:4] != 'http' else introduction_url
        bidding_record_url = 'http:' + bidding_record_url if bidding_record_url[:4] != 'http' else bidding_record_url

        # if announcement_url:
        #     announcement_url = 'https:' + announcement_url
        #     yield
        # elif bidding_instructions_url:
        #     announcement = []
        #     bidding_instructions_url = 'https:' + bidding_instructions_url
        #     yield
        # elif introduction_url:
        #     announcement = []
        #     bidding_instructions = []
        #     introduction_url = 'https:' + introduction_url
        #     yield
        # elif bidCount > 0:
        #     announcement = []
        #     bidding_instructions = []
        #     introduction_url = []
        #     yield

        item_dict.update(
            {
                # 'announcement': [],
                'disposalunit': disposalunit,
                # 'introduction': [],
                'file': [],
                'location': location,
                # 'relation': [],
                'auction_phase': auction_phase,
                'mark_up': mark_up,
                'deposits': deposits,
                'delay_period': delay_period,
                # 'bidding_instructions': bidding_instructions,
                'images': img_list,
                'sale_advance_payment': sale_advance_payment,
                'auction_type': auction_type,
                'videos': videos,
            }
        )
        meta = {
            'detail_id': detail_id,
            'bidCount': bidCount,
            'item_dict': item_dict,
            'bidding_instructions_url': bidding_instructions_url,
            'introduction_url': introduction_url,
            'bidding_record_url': bidding_record_url,
            'file_url': file_url,
        }
        yield scrapy.Request(announcement_url, callback=self.get_notice_attach, meta=meta)

    def extrac_info(self, response, keyword):
        info_list = response.xpath('//span[contains(text(), "{}")]/following-sibling::span[1]//text()'.format(keyword)).extract()
        if info_list:
            info = ''.join(info_list)
            return re.sub(':|：|¥|,', '', info).strip()
        else:
            return ''

    def get_notice_attach(self, response):
        # print(response.url)
        # print(response.text)

        meta = response.meta
        detail_id = meta['detail_id']
        bidCount = meta['bidCount']
        item_dict = meta['item_dict']
        bidding_instructions_url = meta['bidding_instructions_url']
        introduction_url = meta['introduction_url']
        bidding_record_url = meta['bidding_record_url']
        file_url = meta['file_url']
        try:
            resp_json = json.loads(response.text.strip().replace('null(', '').rstrip(');'), encoding='utf-8')
            content = resp_json.get('content', '') or ''
            announcement = common.filter_tags(re.sub('<a.*?>|</a>', '', content), response.url)
            announcement = re.findall('<p>.*?</p>', announcement)

            tree = etree.HTML(content)
            date_list = re.findall('.{4}年.{1,3}月.{1,3}日', tree.xpath("string(/)"))
            publish_date = date_list[-1] if date_list else ''

            item_file = []
            attaches = resp_json.get('attaches', [])
            if attaches:
                for attache in attaches:
                    attache_id = attache.get('id')
                    if attache_id:
                        download_attach_url = 'http://sf.taobao.com/download_attach.do?attach_id={}'.format(attache_id)
                        item_file.append(download_attach_url)

                        # 上传附件
                        upload_result = common.upload_file(download_attach_url)
                        # print('上传附件，detail_id：{}，{}'.format(detail_id, upload_result))
                        if upload_result == 0:
                            self.logger.error('detail_id: {}, 上传附件失败!!!'.format(detail_id))

            announcement = [''.join(announcement)]
            item_dict['announcement'] = announcement
            item_dict['publish_date'] = publish_date
            item_dict['file'] = item_file
            meta = {
                'detail_id': detail_id,
                'bidCount': bidCount,
                'item_dict': item_dict,
                'bidding_instructions_url': bidding_instructions_url,
                'introduction_url': introduction_url,
                'bidding_record_url': bidding_record_url,
                'file_url': file_url,
            }
            yield scrapy.Request(bidding_instructions_url, callback=self.get_notice, meta=meta)
        except:
            self.logger.error(detail_id + ' 竞买公告出错 ' + traceback.format_exc())
            raise exceptions.DropItem

    def get_notice(self, response):
        # print(response.url)
        # print(response.text)

        meta = response.meta
        detail_id = meta['detail_id']
        bidCount = meta['bidCount']
        item_dict = meta['item_dict']
        bidding_instructions_url = meta['bidding_instructions_url']
        introduction_url = meta['introduction_url']
        bidding_record_url = meta['bidding_record_url']
        file_url = meta['file_url']

        resp_json = json.loads(response.text.strip().replace('callback(', '').rstrip(')'), encoding='utf-8')
        content = resp_json.get('content', '') or ''
        bidding_instructions = common.filter_tags(re.sub('<a.*?>|</a>', '', content), response.url)
        bidding_instructions = re.findall('<p>.*?</p>', bidding_instructions)
        bidding_instructions = [''.join(bidding_instructions)]
        item_dict['bidding_instructions'] = bidding_instructions

        meta = {
            'detail_id': detail_id,
            'bidCount': bidCount,
            'item_dict': item_dict,
            'bidding_instructions_url': bidding_instructions_url,
            'introduction_url': introduction_url,
            'bidding_record_url': bidding_record_url,
            'file_url': file_url,
        }

        if introduction_url:
            yield scrapy.Request(introduction_url, callback=self.get_desc, meta=meta)
        else:
            yield scrapy.Request(bidding_record_url, callback=self.get_bid_records, meta=meta)

    def get_desc(self, response):
        # print(response.url)
        # print(response.text)

        meta = response.meta
        detail_id = meta['detail_id']
        bidCount = meta['bidCount']
        item_dict = meta['item_dict']
        bidding_instructions_url = meta['bidding_instructions_url']
        introduction_url = meta['introduction_url']
        bidding_record_url = meta['bidding_record_url']
        file_url = meta['file_url']
        
        # m_desc = re.search("var desc=\\'(.*?)\\';", response.text.strip(), re.M | re.S)
        m_desc = re.search("var desc=\\'(.*?)\\';", response.text.strip().replace("\\", ""), re.M | re.S)
        if m_desc:
            desc = m_desc.group(1)

            try:
                # table_dict = common.extract_table(desc)
                table_dict, table_list = common.extract_table_new(desc)
            except:
                self.logger.error(detail_id + ' 标的物介绍出错')
                raise exceptions.DropItem
            if table_dict:
                item_dict.update(self.get_field_info(table_dict, table_list))
                # relation = self.get_info_from_dict(table_dict, ['所有人', '产权人为', '所有权人']).replace('<p>', '').replace('</p>', '')
                # item_dict['relation'] = [relation] if relation else []
                # item_dict['disposal_basis'] = self.get_info_from_dict(table_dict, ['权利来源', '处置依据', '拍卖依据']).replace('<p>', '').replace('</p>', '')
                # item_dict['authority_card'] = self.get_info_from_dict(table_dict, ['权证情况']).replace('<p>', '').replace('</p>', '')
                # item_dict['sales_actuality'] = self.get_info_from_dict(table_dict, ['现状'])
                # # item_dict['sales_actuality'] = '<p>{}</p>'.format(sales_actuality) if sales_actuality else ''
                # item_dict['restriction_of_rights'] = self.get_info_from_dict(table_dict, ['权利限制'])
                # # item_dict['restriction_of_rights'] = '<p>{}</p>'.format(restriction_of_rights) if restriction_of_rights else ''
                # item_dict['clinch_deal_file'] = self.get_info_from_dict(table_dict, ['提供的文件'])
                # # item_dict['clinch_deal_file'] = '<p>{}</p>'.format(clinch_deal_file) if clinch_deal_file else ''
                # 
                # # lots_introduce = self.get_info_from_dict(table_dict, ['标的物介绍', '拍品介绍', '标的情况', '标的物基本信息'])
                # # item_dict['lots_introduce'] = '<p>{}</p>'.format(lots_introduce) if lots_introduce else ''
                # item_dict['lots_introduce'] = ''
                # for k, v in table_dict.items():
                #     if re.search('|'.join(['标的物介绍', '拍品介绍', '标的情况', '标的物基本信息']), k):
                #         if v.strip():
                #             item_dict['lots_introduce'] = v.strip()
                #         else:
                #             lots_introduce = ''
                #             len_table_list = len(table_list)
                #             for index, each_p in enumerate(table_list):
                #                 m = re.search('<p>.*?(标的物介绍|拍品介绍|标的情况|标的物基本信息).*?</p>', each_p)
                #                 if m:
                #                     m1 = re.search('<p>.*?(标的物介绍|拍品介绍|标的情况|标的物基本信息).*?</p>(<p>.*</p>)', each_p)
                #                     if m1:
                #                         lots_introduce = m1.group(2)
                #                     else:
                #                         if index >= len_table_list - 1:
                #                             lots_introduce = ''
                #                         else:
                #                             for a in table_list[index + 1:]:
                #                                 if a.strip():
                #                                     lots_introduce = a.strip()
                #                                     break
                #                     break
                #             item_dict['lots_introduce'] = lots_introduce
                #         break

            introduction = common.filter_tags(re.sub('<a.*?>|</a>', '', desc), response.url)
            img_list = re.findall('<img src="(.*?)">', introduction)
            img_list = ['http:' + i for i in img_list if img_list]
            introduction = re.findall('<p>.*?</p>', introduction)
            introduction = [''.join(introduction)]
            item_dict['introduction'] = introduction
            # item_dict['images'] = img_list
            item_dict['images'].extend(img_list)

            # todo 特殊处理
            if detail_id == '598593650410':
                item_dict['authority_card'] = '1、有无房屋所有权证复印件：有 2、有无土地使用权证复印件：有'

            meta = {
                'detail_id': detail_id,
                'bidCount': bidCount,
                'item_dict': item_dict,
                'bidding_instructions_url': bidding_instructions_url,
                'introduction_url': introduction_url,
                'bidding_record_url': bidding_record_url,
                'file_url': file_url,
            }
            yield scrapy.Request(bidding_record_url, callback=self.get_bid_records, meta=meta)
        else:
            self.logger.error(detail_id + ' 标的物介绍出错')
            raise exceptions.DropItem

    def get_bid_records(self, response):
        # print(response.url)
        # print(response.text)

        meta = response.meta
        detail_id = meta['detail_id']
        bidCount = meta['bidCount']
        item_dict = meta['item_dict']
        bidding_instructions_url = meta['bidding_instructions_url']
        introduction_url = meta['introduction_url']
        bidding_record_url = meta['bidding_record_url']
        file_url = meta['file_url']

        if bidCount <= 0:
            if file_url:
                meta = {
                    'detail_id': detail_id,
                    'bidCount': bidCount,
                    'item_dict': item_dict,
                    'bidding_instructions_url': bidding_instructions_url,
                    'introduction_url': introduction_url,
                    'bidding_record_url': bidding_record_url,
                    'file_url': file_url,
                }
                yield scrapy.Request(file_url, callback=self.get_gov_attach, meta=meta)
            else:
                yield item_dict
        else:
            # json.loads(re.sub(r'([a-zA-Z]+):', r'"\1":', re.sub(r'\s', '', response.text)))
            resp_json = json.loads(re.sub(r'([a-zA-Z]+):', r'"\1":', response.text))
            records = resp_json.get('records', []) or []
            for record_item in records:
                # bidTime = int(record_item.get('bidTime', 0))
                # bidTime = common.to_time_str(int(bidTime / 1000)) if bidTime else ''
                price = record_item.get('price', '').strip() or ''
                if price:
                    price = re.sub('\.0', '', price).strip() + '元'
                bidding_record = {
                    'offer_state': common.taobao_bidding_record_dict.get(int(record_item.get('status', 2)), '其它'),
                    'price': price,
                    'bidder': record_item.get('alias', '') or '',
                    'time': record_item.get('date', '') or '',
                }
                item_dict['bidding_record'].append(bidding_record)

            meta = {
                'detail_id': detail_id,
                'bidCount': bidCount,
                'item_dict': item_dict,
                'bidding_instructions_url': bidding_instructions_url,
                'introduction_url': introduction_url,
                'bidding_record_url': bidding_record_url,
                'file_url': file_url,
            }

            # bidCount = resp_json.get('totalCnt', 0) or 0
            records_pages = int(bidCount / 20) if bidCount % 20 == 0 else int(bidCount / 20) + 1
            if self.records_page + 1 <= records_pages:
                self.records_page += 1
                records_url = response.url + '&currentPage={}'.format(self.records_page)
                yield scrapy.Request(records_url, self.get_bid_records, meta=meta)
            else:
                if file_url:
                    meta = {
                        'detail_id': detail_id,
                        'bidCount': bidCount,
                        'item_dict': item_dict,
                        'bidding_instructions_url': bidding_instructions_url,
                        'introduction_url': introduction_url,
                        'bidding_record_url': bidding_record_url,
                        'file_url': file_url,
                    }
                    yield scrapy.Request(file_url, callback=self.get_gov_attach, meta=meta)
                else:
                    yield item_dict

    def get_gov_attach(self, response):
        # print(response.url)
        # print(response.text)

        meta = response.meta
        detail_id = meta['detail_id']
        # bidCount = meta['bidCount']
        item_dict = meta['item_dict']
        # bidding_instructions_url = meta['bidding_instructions_url']
        # introduction_url = meta['introduction_url']
        # bidding_record_url = meta['bidding_record_url']
        # file_url = meta['file_url']
        attaches = json.loads(response.text.strip().replace('null(', '').rstrip(');'), encoding='utf-8')
        item_file = []
        if attaches:
            for attache in attaches:
                attache_id = attache.get('id')
                if attache_id:
                    download_attach_url = 'http://sf.taobao.com/download_attach.do?attach_id={}'.format(attache_id)
                    item_file.append(download_attach_url)

                    # 上传附件
                    upload_result = common.upload_file(download_attach_url)
                    # print('上传附件，detail_id：{}，{}'.format(detail_id, upload_result))
                    if upload_result == 0:
                        self.logger.error('detail_id: {}, 上传附件失败!!!'.format(detail_id))

        item_dict['file'].extend(item_file)
        yield item_dict

    def get_info_from_dict(self, table_dict, keywords):
        # keywords 是 ['所有人', '产权人为', '所有权人']
        # print('|'.join(keywords))
        for k, v in table_dict.items():
            if re.search('|'.join(keywords), re.sub('\s', '', k)):
                return v.strip()
        return ''

    def get_field_info(self, table_dict, table_list):
        field_info_dict = {}
        relation = self.get_info_from_dict(table_dict, ['所有人', '产权人为?', '所有权人']).replace('<p>', '').replace('</p>', '')
        field_info_dict['relation'] = [relation] if relation else []
        field_info_dict['disposal_basis'] = self.get_info_from_dict(table_dict, ['权利来源', '处置依据', '拍卖依据']).replace('<p>', '').replace('</p>', '')
        field_info_dict['authority_card'] = self.get_info_from_dict(table_dict, ['权证情况']).replace('<p>', '').replace('</p>', '')
        field_info_dict['sales_actuality'] = self.get_info_from_dict(table_dict, ['现状'])
        # field_info_dict['sales_actuality'] = '<p>{}</p>'.format(sales_actuality) if sales_actuality else ''
        field_info_dict['restriction_of_rights'] = self.get_info_from_dict(table_dict, ['权利限制'])
        # field_info_dict['restriction_of_rights'] = '<p>{}</p>'.format(restriction_of_rights) if restriction_of_rights else ''
        field_info_dict['clinch_deal_file'] = self.get_info_from_dict(table_dict, ['提供的?文件'])
        # field_info_dict['clinch_deal_file'] = '<p>{}</p>'.format(clinch_deal_file) if clinch_deal_file else ''

        # lots_introduce = self.get_info_from_dict(table_dict, ['标的物?介绍', '拍品介绍', '标的情况', '标的物基本信息'])
        # field_info_dict['lots_introduce'] = '<p>{}</p>'.format(lots_introduce) if lots_introduce else ''
        field_info_dict['lots_introduce'] = ''
        for k, v in table_dict.items():
            # if re.search('|'.join(['标的物?介绍', '拍品介绍', '标的情况', '标的物基本信息']), k):
            if re.search('|'.join(['标的物?介绍', '拍品介绍']), re.sub('\s', '', k)):
                if v.strip():
                    field_info_dict['lots_introduce'] = v.strip()
                else:
                    lots_introduce = ''
                    len_table_list = len(table_list)
                    for index, each_p in enumerate(table_list):
                        # m = re.search('<p>.*?(标的物?介绍|拍品介绍|标的情况|标的物基本信息).*?</p>', each_p)
                        m = re.search('<p>.*?(标的物?介绍|拍品介绍).*?</p>', re.sub('\s', '', each_p))
                        if m:
                            # m1 = re.search('<p>.*?(标的物?介绍|拍品介绍|标的情况|标的物基本信息).*?</p>(<p>.*</p>)', each_p)
                            m1 = re.search('<p>.*?(标的物?介绍|拍品介绍).*?</p>(<p>.*</p>)', re.sub('\s', '', each_p))
                            # m2 = re.search('(<p>.*?(标的物?介绍|拍品介绍).*</p>)', re.sub('\s', '', each_p))
                            if m1:
                                lots_introduce = m1.group(2)
                            # elif m2:
                            #     lots_introduce = m2.group(1)
                            else:
                                if index >= len_table_list - 1:
                                    lots_introduce = ''
                                else:
                                    for a in table_list[index + 1:]:
                                        if a.strip():
                                            lots_introduce = a.strip()
                                            break
                            break
                    field_info_dict['lots_introduce'] = lots_introduce
                break

        return field_info_dict


