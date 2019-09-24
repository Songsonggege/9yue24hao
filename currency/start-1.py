from scrapy.cmdline import execute
import sys
import scrapy
from scrapy.crawler import CrawlerProcess
import os

# 给Python解释器，添加模块新路径 ,将main.py文件所在目录添加到Python解释器
sys.path.append(os.path.join(os.getcwd()))

# 执行scrapy命令 '--nolog'
execute(['scrapy', 'crawl', 'fly2'])
