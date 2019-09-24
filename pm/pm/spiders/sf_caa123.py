# -*- coding: utf-8 -*-
import scrapy
import time
import json
from pm import common
import re
from lxml import etree
# import html
# from bs4 import BeautifulSoup


class SfCaa123Spider(scrapy.Spider):
    name = 'sf_caa123'
    allowed_domains = ['sf.caa123.org.cn']
    start_urls = ['http://sf.caa123.org.cn/caa-web-ws/ws/0.1/lots?start=0&count=12&sortname=&sortorder=&lotStatus=&province=&city=&priceBegin=&priceEnd=&lotMode=&times=&isRestricted=&canLoan=&standardType=&secondaryType=&_={}'.format(int(time.time() * 1000))]
    records_page = 0
    total_page = 0

    def parse(self, response):
        # print(response.url)
        # print(response.text)

        resp_json = json.loads(response.text, encoding='utf-8')
        # 翻页
        if not self.total_page:
            total_page = int(resp_json.get('totalPages'))
            self.total_page = total_page
            # for page in range(self.total_page-2, self.total_page):
            # for page in range(1, 3):
            for page in range(1, self.total_page):
                next_page_url = 'http://sf.caa123.org.cn/caa-web-ws/ws/0.1/lots?start={}&count=12&sortname=&sortorder=&lotStatus=&province=&city=&priceBegin=&priceEnd=&lotMode=&times=&isRestricted=&canLoan=&standardType=&secondaryType=&_={}'.format(page, int(time.time() * 1000))
                yield scrapy.Request(next_page_url, self.parse)

        items = resp_json.get('items', [])
        for each_item in items:
            detail_id = each_item.get('id')
            if detail_id:
                # url = 'http://sf.caa123.org.cn/lot/{}.html'.format(detail_id)
                url = 'http://sf.caa123.org.cn/caa-web-ws/ws/0.1/lot/{}?_={}'.format(detail_id, int(time.time()*1000))
                if url:
                    yield scrapy.Request(url, callback=self.get_detail, meta={'detail_id': detail_id})

        # test
        # detail_id_list = ['2750', '2753', '2714', '2727', '2766', '2735', '2717', '2719', '2712', '2767', '2656', '2720']
        # detail_id_list = ['2727']
        # detail_id_list = ['2723']
        # detail_id_list = ['37']
        # for detail_id in detail_id_list:
        #     url = 'http://sf.caa123.org.cn/caa-web-ws/ws/0.1/lot/{}?_={}'.format(detail_id, int(time.time() * 1000))
        #     if url:
        #         yield scrapy.Request(url, callback=self.get_detail, meta={'detail_id': detail_id})

    def get_detail(self, response):
        # print(response.url)
        # print(response.text)
        detail_id = response.meta['detail_id']
        resp_json = json.loads(response.text, encoding='utf-8')
        url = 'http://sf.caa123.org.cn/lot/{}.html'.format(detail_id)
        uid = common.get_id(url)
        starting_price = str(resp_json.get('startPrice', '') or '')
        if starting_price:
            starting_price = re.sub('\.0', '', starting_price).strip() + '元'
        disposalunit = resp_json.get('court', '')
        startTime = int(resp_json.get('startTime', 0))
        start_date = common.to_time_str(int(startTime / 1000)) if startTime else ''
        endTime = int(resp_json.get('endTime', 0))
        if startTime >= endTime:
            end_date = ''
        else:
            end_date = common.to_time_str(int(endTime / 1000)) if endTime else ''
        evaluationprice = str(resp_json.get('assessPrice', '') or '')
        if evaluationprice:
            evaluationprice = re.sub('\.0', '', evaluationprice).strip() + '元'
        name = resp_json.get('name', '')
        type = resp_json.get('standardType', '')
        current_price = str(resp_json.get('nowPrice', '') or '')
        if current_price:
            current_price = re.sub('\.0', '', current_price).strip() + '元'
        sales_status = common.sales_status_dict.get(resp_json.get('lotStatus'), '其他')
        if sales_status == '其他':
            self.logger.error(response.url + ' sales_status ' + resp_json.get('lotStatus', ''))
        auction_phase = common.auction_phase_dict.get(str(resp_json.get('times', 0)), '其他')
        mark_up = str(int(resp_json.get('rateLadder', 0)) or '')
        if mark_up:
            mark_up = re.sub('\.0', '', mark_up).strip() + '元'
        deposits = str(int(resp_json.get('cashDeposit', 0)) or '')
        if deposits:
            deposits = re.sub('\.0', '', deposits).strip() + '元'
        delay_period = resp_json.get('delayTime', '')
        delay_period = delay_period + '分钟/次' if delay_period else ''
        # sale_advance_payment = current_price if resp_json.get('times', 0) == 3 else ''
        if resp_json.get('times', 0) == 3:
            sale_advance_payment = current_price
            auction_type = '变卖'
        else:
            sale_advance_payment = ''
            auction_type = '拍卖'

        item_dict = {
            'uid': uid,
            'url': url,
            # 'announcement': [],  # 从 get_notice_info 获得
            'starting_price': starting_price,
            'disposalunit': disposalunit,
            'end_date': end_date,
            'evaluationprice': evaluationprice,
            # 'introduction': [],  # 从 get_goods_info 获得
            # 'file': [],  # 从 get_goods_info 获得
            # 'location': '',  # 从 get_goods_info 获得
            'name': name,
            # 'relation': [],  # 从 get_goods_info 获得
            'start_date': start_date,
            'type': type,
            'current_price': current_price,
            'sales_status': sales_status,
            'auction_phase': auction_phase,
            'mark_up': mark_up,
            'deposits': deposits,
            'reserve_price': '',  # 无
            'delay_period': delay_period,
            # 'bidding_instructions': bidding_instructions,  # 从 get_instruction_info 获得
            'margin_notes': [],  # 无
            'bidding_record': [],  # 从 get_records_info 获得
            'preemptor': [],  # 无
            # 'images': [],  # 从 get_goods_info 获得
            'sale_advance_payment': sale_advance_payment,
            'auction_type': auction_type,

            # 'disposal_basis': '',
            # 'authority_card': '',
            # 'sales_actuality': '',
            # 'restriction_of_rights': '',
            # 'clinch_deal_file': '',
            # 'lots_introduce': '',
            # 'videos': '',
            # 'publish_date': '',
        }
        good_url = 'http://sf.caa123.org.cn/caa-web-ws/ws/0.1/goods/lot/{}?_={}'.format(detail_id, int(time.time()*1000))
        yield scrapy.Request(good_url, self.get_goods_info, meta={'item_dict': item_dict, 'detail_id': detail_id})

    def get_goods_info(self, response):
        # print(response.url)
        # print(response.text)
        detail_id = response.meta['detail_id']
        item_dict = response.meta['item_dict']
        resp_json = json.loads(response.text, encoding='utf-8')
        remark = resp_json.get('remark', '')
        introduction = []
        introduction_str = ''
        if remark:
            if '<table' in remark:
                tree = etree.HTML(remark)

                # introduction_str = ' '.join(tree.xpath('//tr//text()'))
                td_str_list = []
                td_list = tree.xpath('//tr//td')
                for td in td_list:
                    td_str = ''.join(td.xpath('.//text()'))
                    # print(td_str)
                    td_str_list.append(td_str)
                introduction_str = ' '.join(td_str_list)

                tr_list = tree.xpath('//tr')
                if tr_list:
                    for tr in tr_list:
                        # tr_str = html.unescape(etree.tostring(tr).decode())
                        tr_str = etree.tostring(tr, encoding='utf-8').decode()
                        introduction.append(common.filter_tags(tr_str, response.url))

                    # for tr in tr_list:
                    #     td_text = ' '.join(tr.xpath('.//text()') or [])
                    #     # if td_text.strip():
                    #     introduction.append('<p>{}</p>'.format(td_text.strip()))

                # td_list = tree.xpath('//td')
                # if td_list:
                #     for td in td_list:
                #         td_text = ''.join(td.xpath('.//text()') or [])
                #         # if td_text.strip():
                #         introduction.append('<p>{}</p>'.format(td_text.strip()))
            else:
                introduction = re.findall('<p.*?</p>', remark)
                # common.filter_tags(remark, response.url)
                # introduction = [common.filter_tags(i, response.url) for i in introduction]
                introduction = [common.filter_tags(re.sub('&nbsp;|<a.*?>|</a>', '', i), response.url) for i in introduction]
                introduction = [i for i in introduction if i]

        enclosures = resp_json.get('enclosures', []) or []
        file = []
        for i in enclosures:
            filePath = 'http://sf.caa123.org.cn' + i.get('filePath') if i.get('filePath') else ''
            # 'http://sf.caa123.org.cn/caa-web-ws/ws/0.1/web/enclosure/download/3339'
            downloadPath = 'http://sf.caa123.org.cn/caa-web-ws/ws/0.1/web/enclosure/download/{}'.format(i.get('filePath')) if i.get('filePath') else ''
            if filePath:
                file.append(filePath)

                # 上传附件
                upload_result = common.upload_file(filePath)
                # print('上传附件，detail_id：{}，{}'.format(detail_id, upload_result))
                if upload_result == 0:
                    self.logger.error('detail_id: {}, 上传附件失败!!!'.format(detail_id))

        introduction_len = len(introduction)
        relation = []
        if '<table' in remark:
            for i in range(introduction_len):
                # "<p>产权人为</p>"  "<p>拍品所有权人</p>"
                if re.search('所有人|产权人为|所有权人', introduction[i]):
                    # m_name = re.search('(所有人|产权人为|所有权人)(.*?)</p>', introduction[i])
                    m_name = re.search('(所有人|产权人为|所有权人)(.*)</p>', introduction[i])
                    if m_name:
                        relation.append(m_name.group(2).replace('</p>', '').replace('<p>', '').strip())
                    # else:
                    #     m_name = re.search('[:：](.*?)</p>', introduction[i])
                    #     if m_name:
                    #         relation.append(m_name.group(1).strip())
                    break

            # if re.search('所有人|产权人为|所有权人', introduction[i]) and i < introduction_len - 1:
            #     if '<table' in remark:
            #         relation.append(introduction[i + 1].replace('<p>', '').replace('</p>', '').strip())
            #     else:
            #         m_name = re.search('[:：](.*?)</p>', introduction[i])
            #         if m_name:
            #             relation.append(m_name.group(1).strip())
            #     break
                # names = re.sub('被执行人|:|：|<p>|</p>', '', introduction[i + 1]).split('、')

        disposal_basis = ''
        if '<table' in remark:
            for i in range(introduction_len):
                # m = re.search('(权利来源|处置依据)(.*?)</p>', introduction[i])
                m = re.search('(权利来源|处置依据|拍卖依据)(.*)</p>', introduction[i])
                if m:
                    disposal_basis = m.group(2).replace('</p>', '').replace('<p>', '').strip()

                # if re.search('权利来源', introduction[i]) and i < introduction_len - 1:
                    # disposal_basis = introduction[i + 1].replace('<p>', '').replace('</p>', '').strip()
                    break

        authority_card = ''
        if '<table' in remark:
            m = re.search('权证情况(.*) .*?(所有人|产权人为|所有权人)', introduction_str)
            if m:
                authority_card = m.group(1).strip()
            else:
                for i in range(introduction_len):
                    # if '<table' in remark:
                    # m = re.search('(权证编号|权证情况)( ?)([:：]?)(.*?)</p>', introduction[i])
                    # m = re.search('权证情况(.*?)</p>', introduction[i])
                    m = re.search('权证情况(.*)</p>', introduction[i])
                    if m:
                        authority_card = m.group(1).replace('</p>', '').replace('<p>', '').strip()

                    # if re.search('权证情况', introduction[i]) and i < introduction_len - 1:
                    #     authority_card = introduction[i + 1].replace('<p>', '').replace('</p>', '').strip()
                        break

        sales_actuality = ''
        if '<table' in remark:
            # m = re.search('<p>.*</p><p>.*?现状.*?</p>(.*)<p>.*?权利限制', ''.join(introduction))
            m = re.search('<p>.*</p><p>.*?现状.*?</p>(.*)<p>权利限制.*?</p>', ''.join(introduction))
            if m:
                sales_actuality = m.group(1).strip()
            else:
                for i in range(introduction_len):
                    # m = re.search('现状(.*?)</p>', introduction[i])
                    m = re.search('现状.*?(<p>.*</p>)', introduction[i])
                    if m:
                        sales_actuality = m.group(1).strip()
                        break

        restriction_of_rights = ''
        if '<table' in remark:
            # m = re.search('<p>.*</p>(<p>.*?权利限制.*)<p>.*?提供的文件', ''.join(introduction))
            m = re.search('<p>.*</p><p>权利限制.*?</p>(.*)<p>.*?提供的文件', ''.join(introduction))
            if m:
                # restriction_of_rights = m.group(1).strip()
                restriction_of_rights = m.group(1).strip()
                restriction_of_rights = re.sub('<p>成交后.*</p>', '', restriction_of_rights)
            else:
                for i in range(introduction_len):
                    # m = re.search('权利限制.*? (.*?)</p>', introduction[i])
                    m = re.search('权利限制.*?(<p>.*</p>)', introduction[i])
                    if m:
                        restriction_of_rights = m.group(1).strip()
                        break

        clinch_deal_file = ''
        if '<table' in remark:
            for i in range(introduction_len):
                m = re.search('提供的文件.*?(<p>.*</p>)', introduction[i])
                if m:
                    clinch_deal_file = m.group(1).strip()
                    break

        lots_introduce = ''
        if '<table' in remark:
            # m = re.search('<p>.*</p>(<p>标的物介绍.*)<p>.*?标的物估值', ''.join(introduction))
            m = re.search('<p>.*</p><p>.*?标的物介绍.*?</p>(.*)<p>.*?标的物估值', ''.join(introduction))
            if m:
                lots_introduce = m.group(1).strip()
            else:
                for i in range(introduction_len):
                    # m = re.search('介绍.*?(<p>.*</p>)', introduction[i])
                    # m = re.search('(<p>.*?介绍.*</p>)', introduction[i])
                    m = re.search('(<p>.*?(标的物介绍|拍品介绍).*?<p>.*</p>)', introduction[i])
                    if m:
                        lots_introduce = m.group(1).strip()
                        # lots_introduce = m.group(2).strip()
                        break
                if not lots_introduce:
                    m = re.search('(<p>(标的物介绍|拍品介绍).*</p>)', ''.join(introduction))
                    if m:
                        lots_introduce = m.group(1).strip()

                    # m = re.search('介绍.*?(<p>.*</p>)', ''.join(introduction))
                    # if m:
                    #     lots_introduce = m.group(1).strip()
                    # else:
                    #     m = re.search('(<p>.*?介绍.*</p>)', ''.join(introduction))
                    #     if m:
                    #         lots_introduce = m.group(1).strip()

        pictures = resp_json.get('pictures', [])
        images = ['http://sf.caa123.org.cn'+i.get('filePath') for i in pictures if i.get('filePath')]

        introduction = [''.join(introduction)]

        item_dict.update({
            'introduction': introduction,
            'file': file,
            'location': resp_json.get('position', ''),
            'relation': relation,
            'images': images,

            'disposal_basis': disposal_basis,
            'authority_card': authority_card,
            'sales_actuality': sales_actuality,
            'restriction_of_rights': restriction_of_rights,
            'clinch_deal_file': clinch_deal_file,
            'lots_introduce': lots_introduce,
            'videos': '',
        })

        notice_url = 'http://sf.caa123.org.cn/caa-web-ws/ws/0.1/notice/lot/{}?_={}'.format(detail_id, int(time.time() * 1000))
        yield scrapy.Request(notice_url, self.get_notice_info, meta={'item_dict': item_dict, 'detail_id': detail_id})

    def get_notice_info(self, response):
        # print(response.url)
        # print(response.text)
        detail_id = response.meta['detail_id']
        item_dict = response.meta['item_dict']
        resp_json = json.loads(response.text, encoding='utf-8')
        announcement = re.findall('<p.*?</p>', resp_json.get('noticeContent', '') or '')
        # announcement = [common.filter_tags(i, response.url) for i in announcement]
        announcement = [common.filter_tags(re.sub('&nbsp;|<a.*?>|</a>', '', i), response.url) for i in announcement]
        announcement = [i for i in announcement if i]
        announcement = [''.join(announcement)]

        tree = etree.HTML(resp_json.get('noticeContent', '') or '')
        date_list = re.findall('.{4}年.{1,3}月.{1,3}日', tree.xpath("string(/)"))
        publish_date = date_list[-1] if date_list else ''

        # soup = BeautifulSoup(resp_json.get('noticeContent', '') or '', 'html.parser')
        # print(soup.text)
        # date_list = re.findall('.{4}年.{1,3}月.{1,3}日', soup.text)

        item_dict['announcement'] = announcement
        item_dict['publish_date'] = publish_date
        instruction_url = 'http://sf.caa123.org.cn/caa-web-ws/ws/0.1/instruction/lot/{}?_={}'.format(detail_id, int(time.time() * 1000))
        yield scrapy.Request(instruction_url, self.get_instruction_info, meta={'item_dict': item_dict, 'detail_id': detail_id})

    def get_instruction_info(self, response):
        # print(response.url)
        # print(response.text)
        detail_id = response.meta['detail_id']
        item_dict = response.meta['item_dict']
        resp_json = json.loads(response.text, encoding='utf-8')
        bidding_instructions = re.findall('<p.*?</p>', resp_json.get('guidance', '') or '')
        # bidding_instructions = [common.filter_tags(i, response.url) for i in bidding_instructions]
        bidding_instructions = [common.filter_tags(re.sub('&nbsp;|<a.*?>|</a>', '', i), response.url) for i in bidding_instructions]
        bidding_instructions = [i for i in bidding_instructions if i]
        bidding_instructions = [''.join(bidding_instructions)]
        item_dict['bidding_instructions'] = bidding_instructions
        records_url = 'http://sf.caa123.org.cn/caa-web-ws/ws/0.1/records/lot/{}?start=0&count=20&_={}'.format(detail_id, int(time.time() * 1000))
        yield scrapy.Request(records_url, self.get_records_info, meta={'item_dict': item_dict, 'detail_id': detail_id})

    def get_records_info(self, response):
        # print(response.url)
        # print(response.text)
        detail_id = response.meta['detail_id']
        item_dict = response.meta['item_dict']
        resp_json = json.loads(response.text, encoding='utf-8')
        totalCount = int(resp_json.get('totalCount', 0))
        if totalCount <= 0:
            yield item_dict
        else:
            for record_item in resp_json.get('items', []):
                bidTime = int(record_item.get('bidTime', 0))
                bidTime = common.to_time_str(int(bidTime / 1000)) if bidTime else ''
                price = str(int(record_item.get('price', 0)) or '')
                if price:
                    price = re.sub('\.0', '', price).strip() + '元'
                bidding_record = {
                    'offer_state': common.bidding_record_dict.get(int(record_item.get('status', 2)), '其它'),
                    'price': price,
                    'bidder': record_item.get('bidNum', ''),
                    'time': bidTime,
                }
                item_dict['bidding_record'].append(bidding_record)

            # if totalCount % 20 == 0:
            #     records_pages = int(totalCount / 20)
            # else:
            #     records_pages = int(totalCount / 20) + 1
            records_pages = int(totalCount / 20) if totalCount % 20 == 0 else int(totalCount / 20) + 1
            if self.records_page + 1 < records_pages:
                self.records_page += 1
                records_url = 'http://sf.caa123.org.cn/caa-web-ws/ws/0.1/records/lot/{}?start={}&count=20&_={}'.format(
                    detail_id, self.records_page, int(time.time() * 1000))
                yield scrapy.Request(records_url, self.get_records_info, meta={'item_dict': item_dict, 'detail_id': detail_id})
            else:
                yield item_dict







