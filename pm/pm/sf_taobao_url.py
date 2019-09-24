# coding: utf-8
from pm.common import date_offset


# {'_todo': '即将开始', 'doing': '正在拍卖', 'done': '已成交', 'failure': '已流拍',  'break': '已中止', 'revocation': '已撤回'}
# 正在进行  即将开始  已结束  中止  撤回


def generate_url(start_date, end_date, interval, url_pattern):
    if int(start_date.replace('-', '')) > int(end_date.replace('-', '')):
        yield ''
    else:
        while True:
            interval_date = date_offset(start_date, interval)
            if int(interval_date.replace('-', '')) > int(end_date.replace('-', '')):
                if int(start_date.replace('-', '')) <= int(end_date.replace('-', '')):
                    url = url_pattern.format(start_date, end_date)
                    yield url
                break
            else:
                url = url_pattern.format(start_date, interval_date)
                start_date = date_offset(start_date, interval + 1)
                yield url


# 已撤回
def get_revocation_url(now_date):
    # 从 2013-07-01 开始到现在的2个月后，有数据
    url_pattern = 'https://sf.taobao.com/item_list.htm?auction_source=0&sorder=5&st_param=-1&auction_start_seg=0&auction_start_from={}&auction_start_to={}'
    start_date_1 = date_offset(now_date, 1)
    end_date_1 = date_offset(now_date, 60)
    
    url_list = [
        'https://sf.taobao.com/item_list.htm?auction_source=0&sorder=5&st_param=-1&auction_start_seg=0&auction_start_from=2013-07-01&auction_start_to=2015-12-31',
        'https://sf.taobao.com/item_list.htm?auction_source=0&sorder=5&st_param=-1&auction_start_seg=0&auction_start_from=2016-01-01&auction_start_to=2016-12-31',
        'https://sf.taobao.com/item_list.htm?auction_source=0&sorder=5&st_param=-1&auction_start_seg=0&auction_start_from=2017-01-01&auction_start_to=2017-05-31',

        url_pattern.format(start_date_1, end_date_1),
    ]
    for url in url_list:
        yield url

    start_date = '2017-06-01'
    end_date = now_date
    interval = 30
    # print('start_date:', start_date)
    # print('end_date:', end_date)
    for url in generate_url(start_date, end_date, interval, url_pattern):
        if url:
            yield url


# 正在进行
def get_doing_url(now_date):
    # 从2个月前到现在，有数据
    before_interval = 62
    later_interval = 0
    interval = 10
    start_date = date_offset(now_date, 0 - before_interval)
    url_pattern = 'https://sf.taobao.com/item_list.htm?auction_source=0&sorder=0&st_param=-1&auction_start_seg=&auction_start_from={}&auction_start_to={}'
    for url in generate_url(start_date, now_date, interval, url_pattern):
        if url:
            yield url


# 已结束
def get_over_url(now_date):
    # 从 2012-07-01 开始到现在，有数据
    yield 'https://sf.taobao.com/item_list.htm?auction_source=0&sorder=2&st_param=-1&auction_start_seg=&auction_start_from=2012-07-01&auction_start_to=2013-11-30'
    url_pattern = 'https://sf.taobao.com/item_list.htm?auction_source=0&sorder=2&st_param=-1&auction_start_seg=&auction_start_from={}&auction_start_to={}'

    start_date = '2013-12-01'
    end_date = '2014-11-30'
    interval = 15
    # print('start_date:', start_date)
    # print('end_date:', end_date)
    for url in generate_url(start_date, end_date, interval, url_pattern):
        if url:
            yield url

    # print(11111111)
    start_date = '2014-12-01'
    end_date = '2016-10-31'
    interval = 5
    for url in generate_url(start_date, end_date, interval, url_pattern):
        if url:
            yield url

    # print(11111111)
    start_date = '2016-11-01'
    end_date = now_date
    interval = 1
    for url in generate_url(start_date, end_date, interval, url_pattern):
        if url:
            yield url


# 已中止
def get_break_url(now_date):
    # 从 2013-10-01 开始到现在的2个月后，有数据
    url_pattern = 'https://sf.taobao.com/item_list.htm?auction_source=0&sorder=4&st_param=-1&auction_start_seg=&auction_start_from={}&auction_start_to={}'
    start_date_1 = date_offset(now_date, 1)
    end_date_1 = date_offset(now_date, 60)
    url_list = [
        'https://sf.taobao.com/item_list.htm?auction_source=0&sorder=4&st_param=-1&auction_start_seg=&auction_start_from=2013-10-01&auction_start_to=2016-12-31',
        'https://sf.taobao.com/item_list.htm?auction_source=0&sorder=4&st_param=-1&auction_start_seg=&auction_start_from=2017-01-01&auction_start_to=2017-06-30',
        'https://sf.taobao.com/item_list.htm?auction_source=0&sorder=4&st_param=-1&auction_start_seg=&auction_start_from=2017-07-01&auction_start_to=2017-09-30',
        'https://sf.taobao.com/item_list.htm?auction_source=0&sorder=4&st_param=-1&auction_start_seg=&auction_start_from=2017-10-01&auction_start_to=2017-12-31',
        url_pattern.format(start_date_1, end_date_1),
    ]
    for url in url_list:
        yield url

    start_date = '2018-01-01'
    end_date = now_date
    interval = 30
    # print('start_date:', start_date)
    # print('end_date:', end_date)
    for url in generate_url(start_date, end_date, interval, url_pattern):
        if url:
            yield url


# 即将开始
def get_todo_url(now_date):
    # 从现在到181天后
    before_interval = 0
    later_interval_1 = 31
    later_interval_2 = 150
    interval_1 = 1
    start_date_1 = now_date
    end_date_1 = date_offset(start_date_1, later_interval_1)
    # print('start_date_1:', start_date_1)
    # print('end_date_1:', end_date_1)
    url_pattern = 'https://sf.taobao.com/item_list.htm?auction_source=0&sorder=1&st_param=-1&auction_start_seg=0&auction_start_from={}&auction_start_to={}'
    for url in generate_url(start_date_1, end_date_1, interval_1, url_pattern):
        if url:
            yield url

    # print(1111111)
    start_date_2 = date_offset(start_date_1, later_interval_1 + 1)
    end_date_2 = date_offset(start_date_1, later_interval_1 + later_interval_2)
    interval_2 = 30
    # print('start_date_2:', start_date_2)
    # print('end_date_2:', end_date_2)
    yield url_pattern.format(start_date_2, end_date_2)
    # for url in generate_url(start_date_2, end_date_2, interval_2, url_pattern):
    #     if url:
    #         yield url


# def get_todo_url_o(now_date):
#     before_interval = 0
#     later_interval_1 = 31
#     later_interval_2 = 150
#     interval_1 = 1
#     interval_2 = 30
#     # start_date = date_offset(now_date, 0 - before_interval)
#     start_date = now_date
#     end_date_1 = date_offset(start_date, later_interval_1)
#     print('end_date_1:', end_date_1)
#
#     start_date_2 = date_offset(start_date, later_interval_1 + 1)
#     print('start_date_2:', start_date_2)
#     end_date_2 = date_offset(start_date, later_interval_1 + later_interval_2)
#     # print(end_date_2)
#     print('start_date:', start_date)
#
#     while True:
#         end_date = date_offset(start_date, interval_1)
#         url = 'https://sf.taobao.com/item_list.htm?auction_source=0&sorder=1&st_param=-1&auction_start_seg=0&auction_start_from={}&auction_start_to={}'.format(
#             start_date, end_date)
#         yield url
#         start_date = date_offset(start_date, interval_1 + 1)
#         if int(end_date.replace('-', '')) > int(end_date_1.replace('-', '')):
#             break
#
#     print('start_date_2:', start_date_2)
#     while True:
#         end_date = date_offset(start_date_2, interval_2)
#         url = 'https://sf.taobao.com/item_list.htm?auction_source=0&sorder=1&st_param=-1&auction_start_seg=0&auction_start_from={}&auction_start_to={}'.format(
#             start_date_2, end_date)
#         yield url
#         start_date_2 = date_offset(start_date_2, interval_2 + 1)
#         if int(end_date.replace('-', '')) > int(end_date_2.replace('-', '')):
#             break
#     print('start_date_2:', start_date_2)
    

if __name__ == '__main__':
    now_date = '2019-08-16'
    for i in get_doing_url(now_date):
        print(i)

    # for i in get_todo_url(now_date):
    #     print(i)

    # for i in get_over_url(now_date):
    #     print(i)



