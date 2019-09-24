# -*- coding: utf-8 -*-
import scrapy
from ..items import CfxkItem


class CbrcCfSpider(scrapy.Spider):
    name = 'cbrc_cf'
    allowed_domains = ['www.cbrc.gov.cn']
    start_urls = ['http://www.cbrc.gov.cn/chinese/home/docViewPage/110002&current=1']
    url_fy = 'http://www.cbrc.gov.cn/chinese/home/docViewPage/110002&current='
    offset = 0

    def parse(self, response):
        # p = response.body.decode()
        # print(response.url)

        # 获取所有处罚的链接地址,将职位连接地址加入调度器，请求结果用过callback指定交给next_parse来处理
        tr_list = response.xpath('/ html / body / div[2] / div / div[2] / div / div[2] / table / tr ')
        for tr in tr_list:
            next_url = 'http://www.cbrc.gov.cn' + tr.xpath('./ td[1] / a/@href').get()
            # print(next_url)
           # 获取发布时间
            createdAt = tr.xpath('./td[2]/text()').get()
            # print(createdAt)
            name = tr.xpath('./td[1]/a/text()').get()
            yield scrapy.Request(url=next_url, callback=self.cf_prase, meta={'name':name,'createdAt':createdAt },dont_filter=True)

        #提取下一页的url地址，交个调度器请求，请求的结果还是交给这个函数处理
            if self.offset <= 3:
                self.offset +=1
                yield scrapy.Request(self.url_fy + str (self.offset ),callback=self.parse)

    def cf_prase(self,response):
        createdAt = response.meta.get('createdAt').strip()
        name = response.meta.get('name')
        #获取所有的tr
        tr_list = response.xpath('//table[@class = "MsoNormalTable"]//tr')
        for tr in tr_list:
            td1_text= tr.xpath('./td[1]/p//span[1]/text()').get()

            if '行政处罚决定书文号' in td1_text:
                # 行政处罚决定书文号
                # 编号/编码/
                # identifier1 = response.xpath('/html/body/center/div[3]/div[1]/div/div/table/tr[1]/td/table/tr[2]/td/div/div/table/tr[1]/td[2]/p')
                identifier1 = tr.xpath('./td[last()]//p')
                identifier =  identifier1.xpath('string(.)').get()
            elif '法定代表人姓名' in td1_text:
                # 法人代表/html/body/center/div[3]/div[1]/div/div/table/tbody/tr[1]/td/table/tbody/tr[2]/td/div/div/table/tbody/tr[4]/td[2]/p/span[1]
                # prLegalPerson1 = response.xpath('/html/body/center/div[3]/div[1]/div/div/table/tr[1]/td/table/tr[2]/td/div/div/table/tr[4]/td[2]/p')
                prLegalPerson1 = tr.xpath('./td[last()]//p')
                prLegalPerson= prLegalPerson1.xpath('string(.)').get()
            elif '名称' in td1_text:
                #被处罚主体pip(?浙商银行股份有限公司？)
                # prPrincipa2 =response.xpath('/html/body/center/div[3]/div[1]/div/div/table/tr[1]/td/table/tr[2]/td/div/div/table/tr[3]/td[3]/p')
                prPrincipa2 = tr.xpath('./td[last()]//p')
                prPrincipal = prPrincipa2.xpath('string(.)').get()
            elif '主要违法违规事实' in td1_text:
                # 处罚事由
                prCause1 =tr.xpath('./td[last()]//p')
                # prCause1 = response.xpath('/html/body/center/div[3]/div[1]/div/div/table/tr[1]/td/table/tr[2]/td/div/div/table/tr[5]/td[2]/p')
                prCause = prCause1.xpath('string(.)').get()
            elif '行政处罚依据' in td1_text:
                # 处罚依据
                prGist1 = tr.xpath('./td[last()]//p')
                # prGist1 = response.xpath('/html/body/center/div[3]/div[1]/div/div/table/tr[1]/td/table/tr[2]/td/div/div/table/tr[6]/td[2]/p')
                prGist = prGist1.xpath('string(.)').get()
            elif '行政处罚决定' in td1_text:
                # 处罚结果
                prTarget1= tr.xpath('./td[last()]//p')
                # prTarget1 = response.xpath( '/html/body/center/div[3]/div[1]/div/div/table/tr[1]/td/table/tr[2]/td/div/div/table/tr[7]/td[2]/p')
                prTarget = prTarget1.xpath('string(.)').get()
            elif '作出处罚决定的机关名称' in td1_text:
                #发布方(处罚方)
                publisher1= tr.xpath('./td[last()]//p')
                # publisher1 = response.xpath('/html/body/center/div[3]/div[1]/div/div/table/tr[1]/td/table/tr[2]/td/div/div/table/tr[8]/td[2]/p')
                publisher = publisher1.xpath('string(.)').get()

            else:

                # 处罚日期
                prPunishmentAt1 = tr.xpath('./td[last()]//p')
                # prPunishmentAt1 = response.xpath('/html/body/center/div[3]/div[1]/div/div/table/tr[1]/td/table/tr[2]/td/div/div/table/tr[9]/td[2]/p')
                prPunishmentAt = prPunishmentAt1.xpath('string(.)').get()

                item = CfxkItem(
                    createdAt=createdAt,
                    prLegalPerson=prLegalPerson,
                    prPrincipal=prPrincipal,
                    prCause=prCause,
                    prGist=prGist,
                    prTarget=prTarget,
                    publisher=publisher,
                    prPunishmentAt=prPunishmentAt,
                    identifier=identifier

                )

                yield item




