# author:胡已源
# datetime:2019/8/7 下午1:14
# software: PyCharm

import os
import json
import datetime
import traceback
import inspect
import logging

logger = logging.getLogger('async_spider_reporter')


class InfoLogLogstashFormatter(logging.Formatter):
    """
    输出Json格式的信息，Json包含message以及来自extra参数的字段，对于包含异常的信息，处罚
    异常的简要说明（异常的名称，出现位置等）

    """

    def format(self, record):
        extra = record.__dict__
        record.message = record.getMessage()
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)
        s = self.formatMessage(record)
        if record.exc_info:
            exc_text = self.formatException(record.exc_info)
            if s[-1:] != "\n":
                s = s + "\n"
            s = exc_text + s

        s = {
            "spider": extra.get("spider", "undefined"),
            "action": extra.get("action", "undefined"),
            "step": extra.get("step", "undefined"),
            "item_type": extra.get("item_type", "undefined"),
            "spider_ident": extra.get("spider_ident", "undefined"),
            "url": extra.get("url", "undefined"),
            "message": s,
            "process": extra.get("process", "undefined"),
            "@timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fz"),
            "levelname": extra.get("levelname", "undefined"),
        }

        if "extra_data" in extra:
            s["extra_data"] = extra["extra_data"]
        return json.dumps(s)

    def formatException(self, ei):
        type, value, tb = ei
        r = traceback.extract_tb(tb, limit=None)[-1]
        s = "Exception in file {} line {}, Reason: {} Message:".format(
            r.filename, r.lineno, value
        )

        return s


def get_logger_settings(log_dir, console_output=True):
    logger_settings = {
        'version': 1,
        'disable_existing_logger': False,
        'formatters': {
            # For Normal log,info ,debug,error....
            'logstash_log': {
                '()': '_crawler.logger.InfoLogLogstashFormatter'
            },
            'debug': {
                'format': ('%(asctime)-6s:%(name)s - %(levelname)s - '
                           '%(message)s; %(thread)d - %(filename)s - '
                           '%(funcName)s'),
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'debug'
            },

            'logsatsh_file': {
                'level': 'INFO',
                'class': 'logging.handlers.WatchedFileHandler',
                'formatter': 'logstash_log',
                'filename': os.path.join(log_dir, 'error.log')
            },

            'debug_file': {
                'level': 'DEBUG',
                'class': 'logging.handlers.WatchedFileHandler',
                'formatter': 'debug',
                'filename': os.path.join(log_dir, 'debug.log')
            },
            'error_file': {
                'level': 'ERROR',
                'class': 'logging.handlers.WatchedFileHandler',
                'formatter': 'debug',
                'filename': os.path.join(log_dir, 'error.log')
            }
        },
        'loggers': {
            'async_spider_reporter': {
                'handlers': ['logsatsh_file', 'debug_file'],
                'level': 'INFO',
                'propagate': False
            },
        },
        'root': {
            'handlers': ['debug_file', 'error_file'],
            'level': 'INFO'
        }
    }

    if console_output:
        logger_settings["root"]["handlers"].insert(0, "console")
        logger_settings["loggers"]["async_spider_reporter"]["handlers"].insert('0', "console")

    return logger_settings


def log_parse_start(spider='', spider_ident='', url='', action=''):
    action = action or inspect.currentframe().f_back.f_code.co_name
    spider_name = spider if isinstance(spider, str) else spider.name
    logger.info('parse process start for %s', spider_ident, extra={
        'spider': spider_name,
        'action': action,
        'step': 'parse_start',
        'url': url
    })


def log_parse_success(spider='', spider_ident='', url='', action=''):
    action = action or inspect.currentframe().f_back.f_code.co_name
    spider_name = spider if isinstance(spider, str) else spider.name
    logger.info('parse process success for %s', url, extra={
        'spider': spider_name,
        'action': action,
        'spider_ident': spider_ident,
        'step': 'parse_end',
        'url': url
    })


def log_item_success(
        spider='', spider_ident='', url='', item_type='', item_id=''):
    action = inspect.currentframe().f_back.f_code.co_name
    spider_name = spider if isinstance(spider, str) else spider.name
    logger.info('parse process success for %s', spider_ident, extra={
        'spider': spider_name,
        'action': action,
        'spider_ident': spider_ident,
        'step': 'item_success',
        'url': url,
        'item_type': item_type,
        'item_id': str(item_id)
    })


def log_error(spider='', action='', spider_ident='', url='', reason=''):
    spider_name = spider if isinstance(spider, str) else spider.name
    logger.error('parse process success for %s, reason: %s',
                 spider_ident, reason,
                 extra={
                     'spider': spider_name,
                     'action': action,
                     'spider_ident': spider_ident,
                     'url': url
                 })


def catch_exception_and_log(func):
    print(func)

    def wrapper(*args, **kwargs):
        spider = args[0]
        print(spider)
        if len(args) >= 2:
            response = args[1]
            response_url = response.url
        else:
            response_url = ''
        action = func.__name__
        try:
            log_parse_start(spider, url=response_url, action=action)
            # for ret in func(*args, **kwargs):
            #     yield ret
            log_parse_success(spider, url=response_url, action=action)
        except:
            logger.exception('parse process exception for %s', spider.name,
                             extra={
                                 'spider': spider.name,
                                 'step': 'success',
                                 'url': response_url
                             })

    return wrapper()
