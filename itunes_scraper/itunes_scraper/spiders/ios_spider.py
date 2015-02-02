import scrapy

from scrapy.contrib.spiders import CrawlSpider
from scrapy.selector import Selector

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
		Parses information from iTunes on a single app using the response URL.

		Args:
			response: the HTTP response used to parse app information
		"""
		item = ItunesItem()
		sel = Selector(response)

		item['id'] = response.url[response.url.find('/id') + 3:]

		title = sel.xpath('//div[@id="title"]')
		item['name'] = title.xpath('.//h1/text()').extract()[0]
		item['developer'] = title.xpath('.//h2/text()').extract()[0]

		item['description'] = sel.xpath('//div[h4[contains(text(), "Description")]]/p/text()').extract()[0]
		item['whats_new'] = sel.xpath('//div[h4[contains(text(), "What\'s New")]]/p/text()').extract()[0]

		item['category'] = sel.xpath('//li[@class="genre"]/a/text()').extract()[0]
		item['release_date'] = sel.xpath('//li[@class="release-date"]/text()').extract()[0]
		item['version'] = sel.xpath('//span[contains(text(), "Version")]/../text()').extract()[0]
		item['file_size'] = sel.xpath('//span[contains(text(), "Size")]/../text()').extract()[0]
		item['languages'] = sel.xpath('//li[@class="language"]/text()').extract()[0]
		item['content_advisory_rating'] = sel.xpath('//div[@class="app-rating"]/a/text()').extract()[0]
		item['requirements'] = sel.xpath('//span[@class="app-requirements"]/../text()').extract()[0]

		# Get the rating and number of ratings for the current version and all versions of the app
		customer_ratings = sel.xpath('//div[contains(@class, "customer-ratings")]')
		rating_current_version = customer_ratings.xpath('.//div[contains(text(), "Current Version")]/following-sibling::div[@class="rating"][1]/@aria-label').extract()[0]
		item['rating_current_version'] = rating_current_version.split(',')[0]
		item['num_ratings_current_version'] = rating_current_version.split(',')[1].strip()
		rating_all_versions = customer_ratings.xpath('.//div[contains(text(), "All Versions")]/following-sibling::div[@class="rating"][1]/@aria-label').extract()[0]
		item['rating_all_versions'] = rating_all_versions.split(',')[0]
		item['num_ratings_all_versions'] = rating_all_versions.split(',')[1].strip()

		# Collect the 3 visible reviews for the current version of the app
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

		return item
