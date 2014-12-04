from datetime import datetime
import scrapy

from scrapy import log
from scrapy.contrib.spiders import CrawlSpider
from scrapy.selector import Selector

from android_scraper_2.items import ApkItem

class ApkSpider(CrawlSpider):
	name = 'apkspider'
	allowed_domains = ['play.google.com']

	def __init__(self, package_name=None, *args, **kwargs):
		super(ApkSpider, self).__init__(*args, **kwargs)
		self.start_urls = ['https://play.google.com/store/apps/details?id=%s' % package_name]

	def parse(self, response):
		item = ApkItem()
		sel = Selector(response)

		item['package_name'] = response.url[response.url.find('id=') + 3:]

		info_container = sel.xpath('//div[@class="info-container"]')
		item['name'] = info_container.xpath('//div[@class="document-title"]/div/text()').extract()[0]
		item['developer'] = info_container.xpath('//div[@itemprop="author"]/a/span[@itemprop="name"]/text()').extract()[0]
		item['genre'] = info_container.xpath('//span[@itemprop="genre"]/text()').extract()[0]		

		item['description'] = ''.join(sel.xpath('//div[@class="id-app-orig-desc"]/node()').extract())

		score_container = sel.xpath('//div[@class="score-container"]')
		item['score'] = float(score_container.xpath('//div[@class="score"]/text()').extract()[0])
		item['num_reviews'] = int(score_container.xpath('//span[@class="reviews-num"]/text()').extract()[0].replace(',', ''))

		rating_histogram = sel.xpath('//div[@class="rating-histogram"]')
		item['num_one_star_reviews'] = int(rating_histogram.xpath('//div[@class="rating-bar-container one"]/span[@class="bar-number"]/text()').extract()[0].replace(',', ''))
		item['num_two_star_reviews'] = int(rating_histogram.xpath('//div[@class="rating-bar-container two"]/span[@class="bar-number"]/text()').extract()[0].replace(',', ''))
		item['num_three_star_reviews'] = int(rating_histogram.xpath('//div[@class="rating-bar-container three"]/span[@class="bar-number"]/text()').extract()[0].replace(',', ''))
		item['num_four_star_reviews'] = int(rating_histogram.xpath('//div[@class="rating-bar-container four"]/span[@class="bar-number"]/text()').extract()[0].replace(',', ''))
		item['num_five_star_reviews'] = int(rating_histogram.xpath('//div[@class="rating-bar-container five"]/span[@class="bar-number"]/text()').extract()[0].replace(',', ''))

		item['whats_new'] = ''.join(sel.xpath('//div[@class="recent-change"]/node()').extract())

		additional_information = sel.xpath('//div[@class="details-section metadata"]')
		item['file_size'] = additional_information.xpath('//div[@itemprop="fileSize"]/text()').extract()[0].strip()
		item['version'] = additional_information.xpath('//div[@itemprop="softwareVersion"]/text()').extract()[0].strip()
		item['operating_system'] = additional_information.xpath('//div[@itemprop="operatingSystems"]/text()').extract()[0].strip()
		item['content_rating'] = additional_information.xpath('//div[@itemprop="contentRating"]/text()').extract()[0].strip()

		# Split the range of installs into two concrete values
		num_downloads = additional_information.xpath('//div[@itemprop="numDownloads"]/text()').extract()[0]
		item['lower_installs'] = num_downloads[0:(num_downloads.index('-') - 1)].strip().replace(',', '')
		item['upper_installs'] = num_downloads[num_downloads.index('-') + 1 :].strip().replace(',', '')

		# Convert the date the APK was published from the full month, day, and year to a datetime object
		date_published = additional_information.xpath('//div[@itemprop="datePublished"]/text()').extract()[0]
		item['date_published'] = datetime.strptime(date_published, '%B %d, %Y')

		return item