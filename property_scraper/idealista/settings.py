# -*- coding: utf-8 -*-

# Scrapy settings for idealista project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

from .proxies import get_proxies


###########################
# Main configuration
###########################

BOT_NAME = 'idealista'

SPIDER_MODULES = ['idealista.spiders']
NEWSPIDER_MODULE = 'idealista.spiders'

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
	
    'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
    'scrapy_fake_useragent.middleware.RetryUserAgentMiddleware': 401,	
	
    'scrapy_useragents.downloadermiddlewares.useragents.UserAgentsMiddleware': 500,
	
    'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
    'rotating_proxies.middlewares.BanDetectionMiddleware': 620    
}

DEFAULT_REQUEST_HEADERS = {
    'authority': 'www.idealista.com',
    'upgrade-insecure-requests': '1',
    'sec-fetch-site': 'none',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'sec-fetch-dest':' document'
}

FEED_EXPORT_ENCODING='latin-1'

DOWNLOAD_TIMEOUT = 10


###########################
# User agent configurarion
###########################

FAKEUSERAGENT_PROVIDERS = [
    'scrapy_fake_useragent.providers.FakeUserAgentProvider',  # this is the first provider we'll try
    'scrapy_fake_useragent.providers.FakerProvider',  # if FakeUserAgentProvider fails, we'll use faker to generate a user-agent string for us
    'scrapy_fake_useragent.providers.FixedUserAgentProvider',  # fall back to USER_AGENT value
]

USER_AGENT =  'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36'

USER_AGENTS = [
    ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36'),
    ('Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0')
    
    # Add more user agents which actually work nowadays
]

#########################
# Proxies configuration
#########################

#
# Instructions from https://pypi.org/project/scrapy-rotating-proxies/
#

RETRY_HTTP_CODES = [500, 502, 503, 504, 400, 403, 404, 408]

# ROTATING_PROXY_LIST_PATH takes precedence over ROTATING_PROXY_LIST if both options are present.

#ROTATING_PROXY_LIST = [
#    #'http://proxy0:8888',
#    #'http://user:pass@proxy1:8888',
#    #'https://user:pass@proxy1:8888'
#    'https://185.25.204.195:8989', 
#    'https://109.70.206.42:5678', 
#    'https://195.231.61.100:8118', 
#    'https://151.30.58.26:3128', 
#    'https://188.95.20.139:5678', 
#    'https://185.123.235.107:5678', 
#    'https://31.3.169.77:1080', 
#    'https://195.120.78.30:5678', 
#    'https://151.22.181.205:8080', 
#    'https://31.199.12.150:80', 
#    'https://79.98.1.32:34746', 
#    'https://151.22.181.211:8080', 
#    'https://109.73.184.32:5678', 
#    'https://31.3.178.240:8081', 
#    'https://94.101.55.201:4153', 
#]

ROTATING_PROXY_LIST_PATH = '/home/git/property_scraper/data/proxies.txt'

ROTATING_PROXY_PAGE_RETRY_TIMES = 99999999999 # TODO: is it possible to setup this parameter with no limit?
ROTATING_PROXY_LIST = get_proxies()

# settings.py
#ROTATING_PROXY_BAN_POLICY = 'myproject.policy.MyBanPolicy'

#ROTATING_PROXY_PAGE_RETRY_TIMES = 5
#ROTATING_PROXY_BACKOFF_BASE = 300
#ROTATING_PROXY_BACKOFF_CAP = 3600
#ROTATING_PROXY_BAN_POLICY = 'rotating_proxies.policy.BanDetectionPolicy'

