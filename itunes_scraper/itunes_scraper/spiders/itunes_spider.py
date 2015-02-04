import re

import scrapy

from scrapy.contrib.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request

from itunes_scraper.items import ItunesItem

class ItunesSpider(CrawlSpider):
	name = 'itunes'
	allowed_domains = ['itunes.apple.com']

	def __init__(self):
		"""
		Initializes the iTunesSpider.
		"""
		self.start_urls = ['https://itunes.apple.com/us/genre/ios/id36']

	def parse(self, response):
		"""
		Traverses the iTunes App Store.
		"""
		sel = Selector(response)

		genres = sel.xpath('//div[@id="genre-nav"]/div/ul/li')
		for genre in genres:
			genre_name = genre.xpath('a/text()').extract()[0]
			genre_url = genre.xpath('a/@href').extract()[0]
			yield Request(genre_url, callback=self.parse_genre)

		return

	def parse_genre(self, response):
		"""
		Parses the page of a particular genre (e.g. Books).
		"""
		sel = Selector(response)

		# Traverse the genre by app name
		alphabet = sel.xpath('//div[@id="selectedgenre"]/ul/li')
		for letter in alphabet:
			letter_url = letter.xpath('a/@href').extract()[0]
			yield Request(letter_url, callback=self.parse_letter)

		# Traverse the list of popular apps in the genre
		popular_apps = sel.xpath('//div[@id="selectedcontent"]/ul/li')
		for app in popular_apps:
			app_url = app.xpath('a/@href').extract()[0]
			yield Request(letter_url, callback=self.parse_app) 

		return

	def parse_letter(self, response):
		"""
		Parses a page of apps starting with a particular letter.
		"""
		sel = Selector(response)

		# Traverse the list of apps on the page
		apps = sel.xpath('//div[@id="selectedcontent"]//li')
		for app in apps:
			app_url = app.xpath('a/@href').extract()[0]
			yield Request(app_url, callback=self.parse_app) 

		# Go to the next page
		m = re.match(r'(.*)page=(\d+)', response.url)
		if m is None:
			base_path = response.url
			start_number = 2
		else:
			base_path = m.group(1)
			start_number = int(m.group(2)) + 1
		yield Request(base_path + 'page=' + str(start_number), callback=self.parse_letter)

		return

	def parse_app(self, response):
		"""
		Parses the page of a single app.
		"""
		m = re.match(r'(.*)/id(\d+)(.*)', response.url)
		print m.group(2)
