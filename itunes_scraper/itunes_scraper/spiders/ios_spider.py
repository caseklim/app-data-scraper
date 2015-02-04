import json
import scrapy
from datetime import datetime

from scrapy import log
from scrapy.contrib.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy.exceptions import DropItem

from itunes_scraper.items import ItunesItem

class IosSpider(CrawlSpider):
	name = 'ios'
	allowed_domains = ['itunes.apple.com']

	def __init__(self):
		"""
		Initializes the iOSSpider.
		"""
		self.start_urls = ['https://itunes.apple.com/us/app/kindle-read-books-ebooks-magazines/id302584613']

	def parse(self, response):
		"""
		Parses information from iTunes Preview on a single app.
		"""
		item = ItunesItem()
		sel = Selector(response)

		item['id'] = response.url[response.url.find('/id') + 3:]

		updated_date = sel.xpath('//li[@class="release-date"]/text()').extract()[0]
		item['updated_date'] = datetime.strptime(updated_date, '%b %d, %Y')

		# Collect the 3 visible reviews for the current version of the app
		"""
		item['customer_reviews'] = []
		customer_reviews = sel.xpath('//div[@class="customer-reviews"]/div[@class="customer-review"]')
		for i in range(len(customer_reviews)):
			review = customer_reviews[i]
			item['customer_reviews'].append({
				'title': review.xpath('.//span[@class="customerReviewTitle"]/text()').extract()[0],
				'rating': review.xpath('.//div[@class="rating"]/@aria-label').extract()[0],
				'author': review.xpath('.//span[@class="user-info"]/text()[normalize-space(.)]').extract()[0].split()[1],
				'body': review.xpath('.//p/text()[normalize-space(.)]').extract()[0]
			})
		"""
		
		# Create a request to collect remaining information from the Search API
		request = Request('https://itunes.apple.com/lookup?id=%s' % item['id'], callback=self.parse_search_api)
		request.meta['item'] = item
		return request

	def parse_search_api(self, response):
		"""
		Parses information from the Search API to collect additional information on an app.
		"""
		item = response.meta['item']

		# Parse the JSON received from the Search API in the response body
		try:
			results = json.loads(response.body_as_unicode())['results'][0]

			item['bundle_id'] = results['bundleId']
			item['name'] = results['trackName']
			item['developer'] = results['sellerName']
			item['price'] = results['price']
			item['genre'] = results['primaryGenreName']

			item['description'] = results['description']
			item['release_notes'] = results['releaseNotes']
			
			release_date = results['releaseDate']
			item['release_date'] = datetime.strptime(release_date, '%Y-%m-%dT%H:%M:%SZ')

			item['version'] = results['version']
			item['file_size'] = results['fileSizeBytes']
			item['content_advisory_rating'] = results['contentAdvisoryRating']
			item['minimum_os_version'] = results['minimumOsVersion']

			item['rating_current_version'] = results['averageUserRatingForCurrentVersion']
			item['num_ratings_current_version'] = results['userRatingCountForCurrentVersion']
			item['rating_all_versions'] = results['averageUserRating']
			item['num_ratings_all_versions'] = results['userRatingCount']

			return item
		except Exception as e:
			raise DropItem('%s' % e)
