# -*- coding: utf-8 -*-

# Scrapy settings for itunes_scraper project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

#--------------------
# Scrapy Settings
#--------------------

BOT_NAME = 'itunes_scraper'

SPIDER_MODULES = ['itunes_scraper.spiders']
NEWSPIDER_MODULE = 'itunes_scraper.spiders'

ITEM_PIPELINES = {
	'itunes_scraper.pipelines.MariaDBPipeline': None
}

DOWNLOAD_DELAY = 0.25

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'itunes_scraper (+http://www.yourdomain.com)'

#--------------------
# Custom Settings
#--------------------

# Information used by MariaDBPipeline to connect to a MariaDB database
MARIADB_INFO = {
	'user': 'root',
	'password': 'password',
	'database': 'android_scraper_2'
}
