# -*- coding: utf-8 -*-

# Scrapy settings for currency project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import os

# 它是一种可以用于构建用户代理机器人的名称,默认值:'scrapybot'
BOT_NAME = 'currency'
# 它是一种含有蜘蛛其中Scrapy将寻找模块列表,默认值： []
SPIDER_MODULES = ['currency.spiders']
# 默认: '',使用 genspider 命令创建新spider的模块。
NEWSPIDER_MODULE = 'currency.spiders'

# -----------------------------robots协议---------------------------------------------
# Obey robots.txt rules
# robots.txt 是遵循 Robot协议 的一个文件，它保存在网站的服务器中，它的作用是，告诉搜索引擎爬虫，
# 本网站哪些目录下的网页 不希望 你进行爬取收录。在Scrapy启动后，会在第一时间访问网站的 robots.txt 文件，
# 然后决定该网站的爬取范围。
ROBOTSTXT_OBEY = False

# 对于失败的HTTP请求(如超时)进行重试会降低爬取效率，当爬取目标基数很大时，舍弃部分数据不影响大局，提高效率
RETRY_ENABLED = False
# 请求下载超时时间，默认180秒
DOWNLOAD_TIMEOUT = 180
# 这是响应的下载器下载的最大尺寸，默认值：1073741824 (1024MB)
# DOWNLOAD_MAXSIZE=1073741824
# 它定义为响应下载警告的大小，默认值：33554432 (32MB)
# DOWNLOAD_WARNSIZE=33554432

# ------------------------全局并发数的一些配置:-------------------------------

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# 下载延迟会影响 CONCURRENT_REQUESTS，不能使并发显现出来,设置下载延迟
DOWNLOAD_DELAY = 0.5

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# 默认 Request 并发数：16
CONCURRENT_REQUESTS = 32
# 默认 Item 并发数：100
# CONCURRENT_ITEMS = 100

# The download delay setting will honor only one of:
# 默认每个域名的并发数：8
CONCURRENT_REQUESTS_PER_DOMAIN = 16

# 每个IP的最大并发数：0表示忽略
CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False
# 禁用cookies,有些站点会从cookies中判断是否为爬虫
# COOKIES_DEBUG = True


# Crawl responsibly by identifying yourself (and your website) on the user-agent
# 它定义了在抓取网站所使用的用户代理，默认值：“Scrapy / VERSION“
# USER_AGENT = 'currency (+http://www.yourdomain.com)'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; …) Gecko/20100101 Firefox/62.0'

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#     'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'currency.middlewares.CurrencySpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
# 开启两个下载中间件，并调整HttpCompressionMiddlewares的次序
DOWNLOADER_MIDDLEWARES = {
    'currency.middlewares.RandomUserAgentMiddleware': 543,
    'currency.middlewares.ProxyMiddleware': 544,
    'currency.middlewares.SeleniumMiddleware': 560,
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,  # 关闭scrapy默认UA
}

RANDOM_UA_TYPE = "random"  # 或者指定浏览器 firefox、chrome...
COOKIE_IS_TURN_ON = "china_banking_regulatory_commission"  # 是否打开添加只需执行爬虫

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    # 'currency.pipelines.CurrencyPipeline': 300,
    'currency.pipelines.BaseMongoPipeline': 300,
}

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# ----------------scrapy默认已经自带了缓存，配置如下-----------------
# 打开缓存
# HTTPCACHE_ENABLED = True
# 设置缓存过期时间（单位：秒）
# HTTPCACHE_EXPIRATION_SECS = 0
# 缓存路径(默认为：.scrapy/httpcache)
# HTTPCACHE_DIR = 'httpcache'
# 忽略的状态码
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPERROR_ALLOWED_CODES = [302, 301]
# 缓存模式(文件缓存)
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# mongodb配置信息设置
DEPLOY_MODE = "dev"
MONGODB_DB_NAME = 'beehive'

if DEPLOY_MODE == "Prod":
    MONGO_ADDR = ['127.0.0.1:27017']
    MONGO_AUTH = {
        'name': 'view',
        'password': 'view',
        'mechanism': 'SCRAM-SHA-a',
    }
else:
    MONGO_ADDR = ['172.19.80.55:27017']
    MONGO_AUTH = None
    MONGO_REPLICASET = None
    MOTOR_AUTH = None

# redis配置信息
REDIS_HOST = "127.0.0.1"
REDIS_PORT = "6379"
REDIS_DB_INDEX = 1
REDIS_DB_PWD = "foobared"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ----------------------Selenium配置-------------------------------------

# 执行路径
EXECUTABLE_PATH = "/usr/bin/chromedriver"
# 全局超时时间
SELENIUM_TIMEOUT = 10
# 是否启用开发者模式,开启可以避免被服务检测
DEVELOPER_MODE = True
# 基本参数设定
CHROME_SERVICE_ARGS = [ '--disable-gpu', '--no-sandbox', '--incognito']

# ----------------------splash配置-------------------------------------
# Splash服务器地址
SPLASH_URL = 'http://localhost:8050'
#
# # 用来支持cache_args（可选）
SPIDER_MIDDLEWARES = {
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
}
#
# # 设置去重过滤器
DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'

# 启用scrapy_splash需要开启下面三个中间件配置


# ----------------------redis的地址配置-------------------------------------
# Specify the full Redis URL for connecting (optional).
# If set, this takes precedence over the REDIS_HOST and REDIS_PORT settings.
# 指定用于连接redis的URL（可选）
# 如果设置此项，则此项优先级高于设置的REDIS_HOST 和 REDIS_PORT
# REDIS_URL = 'redis://root:密码@主机ＩＰ:端口'
# REDIS_URL = 'redis://root:123456@192.168.8.30:6379'
REDIS_URL = 'redis://root:%s@%s:%s' % (REDIS_DB_PWD, REDIS_HOST, REDIS_PORT)
# 自定义的redis参数（连接超时之类的）
# REDIS_PARAMS = {'db': db_redis}
# Specify the host and port to use when connecting to Redis (optional).
# 指定连接到redis时使用的端口和地址（可选）
# REDIS_HOST = '127.0.0.1'
# REDIS_PORT = 6379
# REDIS_PASS = '19940225'


# -----------------Scrapy-Redis分布式爬虫相关设置如下--------------------------
# Enables scheduling storing requests queue in redis.
# 启用Redis调度存储请求队列，使用Scrapy-Redis的调度器,不再使用scrapy的调度器
Scrapy_Redis_is_TurnOn = False

if Scrapy_Redis_is_TurnOn:
    SCHEDULER = "scrapy_redis.scheduler.Scheduler"
    # Ensure all spiders share same duplicates filter through redis.
    # 确保所有的爬虫通过Redis去重，使用Scrapy-Redis的去重组件,不再使用scrapy的去重组件
    DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"

    # 默认请求序列化使用的是pickle 但是我们可以更改为其他类似的。PS：这玩意儿2.X的可以用。3.X的不能用
    # SCHEDULER_SERIALIZER = "scrapy_redis.picklecompat"

    # 使用优先级调度请求队列 （默认使用），
    # 使用Scrapy-Redis的从请求集合中取出请求的方式,三种方式择其一即可:
    # 分别按(1)请求的优先级/(2)队列FIFO/(先进先出)(3)栈FILO 取出请求（先进后出）
    # SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.PriorityQueue'
    # 可选用的其它队列
    SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.FifoQueue'
    # SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.LifoQueue'

    # Don't cleanup redis queues, allows to pause/resume crawls.
    # 不清除Redis队列、这样可以暂停/恢复 爬取，
    # 允许暂停,redis请求记录不会丢失(重启爬虫不会重头爬取已爬过的页面)
    # SCHEDULER_PERSIST = True

# -----------------------------------------暂时用不到-------------------------------------------------------
# 它定义了将被允许抓取的网址的长度为URL的最大极限，默认值：2083
# URLLENGTH_LIMIT=2083
# 爬取网站最大允许的深度(depth)值,默认值0。如果为0，则没有限制
# DEPTH_LIMIT = 3
# 整数值。用于根据深度调整request优先级。如果为0，则不根据深度进行优先级调整。
# DEPTH_PRIORITY=3

# 最大空闲时间防止分布式爬虫因为等待而关闭
# 这只有当上面设置的队列类是SpiderQueue或SpiderStack时才有效
# 并且当您的蜘蛛首次启动时，也可能会阻止同一时间启动（由于队列为空）
# SCHEDULER_IDLE_BEFORE_CLOSE = 10

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# 开始下载时限速并延迟时间
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# 高并发请求时最大延迟时间
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# 禁止重定向
# 除非您对跟进重定向感兴趣，否则请考虑关闭重定向。 当进行通用爬取时，一般的做法是保存重定向的地址，并在之后的爬取进行解析。
# 这保证了每批爬取的request数目在一定的数量， 否则重定向循环可能会导致爬虫在某个站点耗费过多资源。
# REDIRECT_ENABLED = False
