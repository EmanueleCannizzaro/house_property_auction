# Scrapy settings for pvp project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'pvp'

SPIDER_MODULES = ['pvp.spiders']
NEWSPIDER_MODULE = 'pvp.spiders'

# while developing we want to see debug logs
LOG_LEVEL = "DEBUG" # or "INFO" in production

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

#SCRAPEOPS_PROXY_ENABLED = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# Max Concurrency On ScrapeOps Proxy Free Plan is 1 thread
CONCURRENT_REQUESTS = 5
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 3
RANDOMIZE_DOWNLOAD_DELAY = True
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# to avoid basic bot detection we want to set some basic headers
DEFAULT_REQUEST_HEADERS = {
    # we should use headers
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'it',
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
	# Add In The ScrapeOps Monitoring Extension
	#'scrapeops_scrapy.extension.ScrapeOpsMonitor': 500,
}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
#    'pvp.middlewares.PvpSpiderMiddleware': 543,
}

DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

PLAYWRIGHT_BROWSER_TYPE = "chromium"

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,

    #'pvp.middlewares.PvpDownloaderMiddleware': 543,
    #'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': None,

    'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,

    ## ScrapeOps Monitor
    #'scrapeops_scrapy.middleware.retry.RetryMiddleware': 550,
    #'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,

    'rotating_free_proxies.middlewares.RotatingProxyMiddleware': 610,
    'rotating_free_proxies.middlewares.BanDetectionMiddleware': 620,
    
    ## Proxy Middleware
    #'scrapeops_scrapy_proxy_sdk.scrapeops_scrapy_proxy_sdk.ScrapeOpsScrapyProxySdk': 725,

    #'scrapy_rotated_proxy.downloadmiddlewares.proxy.RotatedProxyMiddleware': 750,

}

# Path that this library uses to store list of proxies
ROTATING_PROXY_LIST_PATH = 'proxies.txt'
NUMBER_OF_PROXIES_TO_FETCH = 5  # Controls how many proxies to use


# -----------------------------------------------------------------------------
# ROTATED PROXY SETTINGS (Local File Backend)
# -----------------------------------------------------------------------------
#ROTATED_PROXY_ENABLED = True
#PROXY_STORAGE = 'scrapy_rotated_proxy.extensions.file_storage.FileProxyStorage'
#PROXY_FILE_PATH = '../../data/proxies.txt'

FEEDS = {
    # '../../data/%(name)s_%(site_id)_%(time)s.csv'
    '%(name)s_%(time)s.csv': {
        'format': 'csv',
        # 'overwrite': True,
        'encoding': 'utf8',
        'store_empty': False,
        # 'item_classes': [MyItemClass1, 'myproject.items.MyItemClass2'],
        #'fields': None,
        #'indent': 4,
        'item_export_kwargs': {
            'export_empty_fields': True,
        }
    },
    '%(name)s_%(time)s_%(batch_id)d.csv': {
        'format': 'csv',
        # 'overwrite': True,
        #'batch_item_count': 1000,
        'encoding': 'utf8',
        'store_empty': False,
        # 'item_classes': [MyItemClass1, 'myproject.items.MyItemClass2'],
        #'fields': None,
        #'indent': 4,
        'item_export_kwargs': {
            'export_empty_fields': True,
        },
        '%(name)s_%(time)s.json': {
            'format': 'json',
            'overwrite': True
        },
        '%(name)s_%(time)s_%(batch_id)d.jsonl': {
            'format': 'jsonlines',
            'overwrite': True,
            #'batch_item_count': 1000,
            'encoding': 'utf8',
            'store_empty': False,
            # 'item_classes': [MyItemClass1, 'myproject.items.MyItemClass2'],
            #'fields': None,
            'indent': 4,
            'item_export_kwargs': {
                'export_empty_fields': True,
            }
        },
        's3://app-stop-data/property_scraper/%(name)s_%(time)s.csv': {
            'format': 'csv',
            'overwrite': True,
            'encoding': 'utf8',
            'store_empty': False,
            # 'item_classes': [MyItemClass1, 'myproject.items.MyItemClass2'],
            #'fields': None,
            #'indent': 4,
            'item_export_kwargs': {
                'export_empty_fields': True,
            }
        },
        "s3://app-stop-data/property_scraper/%(name)s_%(time)s_%(batch_id)d.jsonl": {
            "format": "jsonlines",
            'overwrite': True,
            #'batch_item_count': 1000,
            'encoding': 'utf8',
            'store_empty': False,
            # 'item_classes': [MyItemClass1, 'myproject.items.MyItemClass2'],
            #'fields': None,
            'indent': 4,
            'item_export_kwargs': {
                'export_empty_fields': True,
            }
        }
    }
}

FEED_STORAGES = {
    '': 'scrapy.extensions.feedexport.FileFeedStorage',
    'file': 'scrapy.extensions.feedexport.FileFeedStorage',
    'stdout': 'scrapy.extensions.feedexport.StdoutFeedStorage',
    's3': 'scrapy.extensions.feedexport.S3FeedStorage',
    'ftp': 'scrapy.extensions.feedexport.FTPFeedStorage',
}

FEED_EXPORTERS = {
    'json': 'scrapy.exporters.JsonItemExporter',
    'jsonlines': 'scrapy.exporters.JsonLinesItemExporter',
    'jsonl': 'scrapy.exporters.JsonLinesItemExporter',
    'jl': 'scrapy.exporters.JsonLinesItemExporter',
    'csv': 'scrapy.exporters.CsvItemExporter',
    'xml': 'scrapy.exporters.XmlItemExporter',
    'marshal': 'scrapy.exporters.MarshalItemExporter',
    'pickle': 'scrapy.exporters.PickleItemExporter',
}

#IMAGES_STORE = '../../www/pvp'
# IMAGES_STORE = 'ftp://one:1234@localhost/ftp/one' # This requires an FTP server running on localhost with username 'one' and password '1234' with the home directory set to '/ftp/one'.
# IMAGES_STORE = 's3://images.scrapy.mydomain.com/' # This requies an S3 bucket with the specified name and valid AWS credentials to upload files to that bucket
IMAGE_STORE = "images" # Using a directory on the local file system called images.
IMAGES_THUMBS = {
    'small': (50, 50),
    'big': (270, 270),
}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    #'scrapy.pipelines.files.FilesPipeline': 1,
    #'scrapy.pipelines.images.ImagesPipeline': 1,
    #'property_scraper.pvp.pipelines.HtmlPipeline': 290,
    #'property_scraper.pvp.pipelines.SqlitePipeline': 300,
    #'property_scraper.pvp.pipelines.SqliteNoDuplicatesPipeline': 310,
    ##'property_scraper.pvp.pipelines.MysqlPipeline': 320,
    #'property_scraper.pvp.pipelines.MysqlNoDuplicatesPipeline': 330,
    ##'property_scraper.pvp.pipelines.PostgresPipeline': 340,
    #'property_scraper.pvp.pipelines.PostgresNoDuplicatesPipeline': 350,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
