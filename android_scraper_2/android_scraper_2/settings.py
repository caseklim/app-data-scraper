# -*- coding: utf-8 -*-

# Scrapy settings for android_scraper_2 project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'android_scraper_2'

SPIDER_MODULES = ['android_scraper_2.spiders']
NEWSPIDER_MODULE = 'android_scraper_2.spiders'

DOWNLOADER_MIDDLEWARES = {
	'android_scraper_2.middlewares.RandomUserAgentMiddleware': None,
	'android_scraper_2.middlewares.ProxyMiddleware': None,
	'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None
}

# Proxies need to be from the USA in order to gather data in English
PROXY_LIST = [

]

USER_AGENT_LIST = [
	'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.13+ (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2',
	'Mozilla/5.0 (Windows; U; Windows NT 5.0; en-US; rv:1.4b) Gecko/20030516 Mozilla Firebird/0.6',
	'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1944.0 Safari/537.36',
	'Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0',
	'Mozilla/5.0 (X11; Linux x86_64; rv:28.0) Gecko/20100101 Firefox/28.0'
]

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'android_scraper_2 (+http://www.yourdomain.com)'
