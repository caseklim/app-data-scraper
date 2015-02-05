import re
import json
import urllib2
import scrapy
from datetime import datetime
from elementtree import ElementTree

from scrapy import log
from scrapy.contrib.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy.exceptions import DropItem

from itunes_scraper.items import ItunesItem

class IosSpider(CrawlSpider):
	name = 'ios'

	def __init__(self):
		"""
		Initializes the iOSSpider.
		"""
		self.start_urls = ['https://itunes.apple.com/us/app/id429047995']

	def parse(self, response):
		"""
		Parses information from iTunes Preview on a single app.
		"""
		item = ItunesItem()
		sel = Selector(response)

		item['id'] = response.url[response.url.find('/id') + 3:]

		updated_date = sel.xpath('//li[@class="release-date"]/text()').extract()[0]
		item['updated_date'] = datetime.strptime(updated_date, '%b %d, %Y')
		
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

			# Collect all customer reviews for the current version of the app
			item['customer_reviews'] = self.get_reviews(143441, item['id'], item['version'])

			return item

		except Exception as e:
			raise DropItem('%s' % e)

	# Thank you to grych on GitHub for the following two functions:

	def get_reviews(self, app_store_id, app_id, app_version):
		"""
		Returns a list of customer reviews for a given App Store ID and app ID.

		Args:
			app_store_id: the corresponding App Store ID number for a particular country
			app_id: unique identifier for the app from which to collect customer reviews
			app_version: version of the app for which to collect customer reviews
		"""
		reviews = []
		i = 0
		while True: 
			ret = self.get_reviews_for_page(app_store_id, app_id, app_version, i)
			if len(ret) == 0:
				break
			reviews += ret
			i += 1
		return reviews

	def get_reviews_for_page(self, app_store_id, app_id, app_version, page_num):
		"""
		Returns a list of customer reviews on a given page for a given app.

		Args:
			app_store_id: the corresponding App Store ID number for a particular country
			app_id: unique identifier for the app from which to collect customer reviews
			app_version: version of the app for which to collect customer reviews
			page_num: current page number
		"""
		userAgent = 'iTunes/9.2 (Macintosh; U; Mac OS X 10.6)'
		front = '%d-1' % app_store_id
		url = 'http://ax.phobos.apple.com.edgesuite.net/WebObjects/MZStore.woa/wa/viewContentsUserReviews?id=%s&pageNumber=%d&sortOrdering=4&onlyLatestVersion=false&type=Purple+Software' % (app_id, page_num)
		request = urllib2.Request(url, headers={'X-Apple-Store-Front': front,'User-Agent': userAgent})
		
		try:
			u = urllib2.urlopen(request, timeout=30)
		except urllib2.HTTPError:
			print 'Can\'t connect to the App Store, please try again later.'
			raise SystemExit
		
		root = ElementTree.parse(u).getroot()
		reviews = []
		for node in root.findall('{http://www.apple.com/itms/}View/{http://www.apple.com/itms/}ScrollView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}View/{http://www.apple.com/itms/}MatrixView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}VBoxView/'):
			review = {}

			review_node = node.find('{http://www.apple.com/itms/}TextView/{http://www.apple.com/itms/}SetFontStyle')
			if review_node is None:
				review['review'] = None
			else:
				review['review'] = review_node.text

			version_node = node.find('{http://www.apple.com/itms/}HBoxView/{http://www.apple.com/itms/}TextView/{http://www.apple.com/itms/}SetFontStyle/{http://www.apple.com/itms/}GotoURL')
			if version_node is None:
				review['version'] = None
			else:
				review['version'] = re.search(r'Version ([^\n^\ ]+)', version_node.tail).group(1)

			# If the review is for a version of the app other than the current one, then skip it
			if review['version'] != app_version:
				continue

			user_node = node.find('{http://www.apple.com/itms/}HBoxView/{http://www.apple.com/itms/}TextView/{http://www.apple.com/itms/}SetFontStyle/{http://www.apple.com/itms/}GotoURL/{http://www.apple.com/itms/}b')
			if user_node is None:
				review['user'] = None
			else:
				review['user'] = user_node.text.strip()

			rating_node = node.find("{http://www.apple.com/itms/}HBoxView/{http://www.apple.com/itms/}HBoxView/{http://www.apple.com/itms/}HBoxView")
			try:
				alt = rating_node.attrib['alt']
				stars = int(alt.strip(' stars'))
				review['rating'] = stars
			except KeyError:
				review['rating'] = None

			topic_node = node.find('{http://www.apple.com/itms/}HBoxView/{http://www.apple.com/itms/}TextView/{http://www.apple.com/itms/}SetFontStyle/{http://www.apple.com/itms/}b')
			if topic_node is None:
				review['topic'] = None
			else:
				review['topic'] = topic_node.text

			reviews.append(review)

		return reviews
