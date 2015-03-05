import re
import scrapy
from datetime import datetime

from scrapy.contrib.spiders import CrawlSpider
from scrapy.selector import Selector

from android_scraper.items import ApkItem

class ApkSpider(CrawlSpider):
	name = 'apk'
	allowed_domains = ['play.google.com']

	def __init__(self, package_name=None, start_time=None, *args, **kwargs):
		"""
		Initializes the ApkSpider.

		Args:
			package_name: the package name of the app to collect information on
			start_time: the time at which the scraping session started
		"""
		super(ApkSpider, self).__init__(*args, **kwargs)
		self.start_urls = ['https://play.google.com/store/apps/details?id=%s' % package_name]
		self.package_name = package_name
		self.start_time = start_time

	def parse(self, response):
		"""
		Parses information from Google Play on a single app using the response URL.
		"""
		item = ApkItem()
		sel = Selector(response)

		# Keep track of the start time that was passed in as an argument
		item['start_time'] = self.start_time

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

		# Collect all reviews for the current version of the app
		item['reviews'] = []
		single_reviews = sel.xpath('//div[@class="single-review"]')
		for i in range(len(single_reviews)):
			review = single_reviews[i]

			# Reviews may be anonymous and display "A Google User" instead, so we need to
			# determine if the review has a user attached to it or not. Later, if the review
			# is anonymous, then "None" will be assigned to the reviewer_id property.
			author_name = review.xpath('./div[@class="review-header"]/div[@class="review-info"]/span[@class="author-name"]')
			author = author_name.xpath('./text()').extract()[0].strip()
			if not author:
				author = author_name.xpath('./a[1]/@href').extract()[0]
			
			# Reviews may not have a title. If so, set the review title to None.
			review_title = None
			try:
				review_title = review.xpath('//span[@class="review-title"]/text()').extract()[i]
			except:
				pass

			review_date = review.xpath('//span[@class="review-date"]/text()').extract()[i]
			review_rating = review.xpath('//div[@class="review-info-star-rating"]//div[1]/@aria-label').extract()[i].strip()
			item['reviews'].append({
				'reviewer_id': int(author[author.find('id=') + 3:]) if author.find('id=') > -1 else None,
				'rating': re.search('Rated (.+?) stars out of five stars', review_rating).group(1),
				'title': review_title,
				'body': review.xpath('//div[@class="review-body"]/text()[normalize-space(.)]').extract()[i].strip(),
				'review_date': datetime.strptime(review_date, '%B %d, %Y')
			})

		# Collect all apps listed as similar to the app
		item['similar_apps'] = sel.xpath('//div[@class="rec-cluster"][1]//div[@class="card no-rationale square-cover apps small"]/./@data-docid').extract()

		# Generate the time at which scraping ended for this app
		now = datetime.now()
		item['end_time'] = now.strftime('%Y-%m-%d %T')

		return item
		