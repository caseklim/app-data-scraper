import mysql.connector as mariadb

from scrapy import log
from scrapy.exceptions import DropItem

# Inserts the APK and its related information into a MariaDB database
class MariaDBPipeline(object):

	# Opens the database connection
	def __init__(self, settings):
		self.new_apk_id = None
		self.db_info = settings.get('MARIADB_INFO')
		self.connection = mariadb.connect(user=self.db_info['user'], password=self.db_info['password'], database=self.db_info['database'])
		self.cursor = self.connection.cursor()

	@classmethod
	def from_crawler(cls, crawler):
		return cls(crawler.settings)

	# Inserts the APK, its reviews, and its similar apps into the database.
	# If an error occurs, the item is dropped. Otherwise, the APK and its
	# related information were successfully inserted into the database.
	def process_item(self, item, spider):
		try:
			self.insert_item(item)
			self.insert_reviews(item)
			self.insert_similar_apps(item)
		except mariadb.Error as error:
			log.msg('Error: {}'.format(error), level=log.ERROR)
		finally:
			self.connection.close()
			return item

	# Inserts the APK into the database
	# TODO: Need crawling_session_id
	def insert_item(self, item):
		log.msg('Inserting %s into apk_information...' % item['package_name'], level=log.INFO)
		self.cursor.execute('INSERT INTO apk_information (package_name, name, developer, date_published, ' +
				'genre, description, score, num_reviews, num_one_star_reviews, num_two_star_reviews, num_three_star_reviews, ' +
				'num_four_star_reviews, num_five_star_reviews, whats_new, file_size, lower_installs, upper_installs, version, ' +
				'operating_system, content_rating) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', 
			(item['package_name'], item['name'], item['developer'], item['date_published'], item['genre'], item['description'], 
				item['score'], item['num_reviews'], item['num_one_star_reviews'], item['num_two_star_reviews'], item['num_three_star_reviews'],
				item['num_four_star_reviews'], item['num_five_star_reviews'], item['whats_new'], item['file_size'], item['lower_installs'],
				item['upper_installs'], item['version'], item['operating_system'], item['content_rating']))
		self.connection.commit()
		self.new_apk_id = self.cursor.lastrowid
		log.msg('Insert complete! %s' % item['package_name'], level=log.INFO)

	# Inserts the APK's reviews into the database
	def insert_reviews(self, item):
		log.msg('Inserting reviews for %s into reviews...' % item['package_name'], level=log.INFO)
		for review in item['reviews']:
			self.cursor.execute('INSERT INTO reviews (apk_id, title, body, reviewer_id, review_date, rating) VALUES (%s, %s, %s, %s, %s, %s)',
				(self.new_apk_id, review['title'], review['body'], review['reviewer_id'], review['review_date'], review['rating']))
		log.msg('Insert of reviews complete! %s' % item['package_name'], level=log.INFO)
		self.connection.commit()

	# Inserts the apps similar to the APK into the database
	def insert_similar_apps(self, item):
		log.msg('Inserting similar apps for %s into similar_apps...' % item['package_name'], level=log.INFO)
		for similar_app in item['similar_apps']:
			self.cursor.execute('INSERT INTO similar_apps (apk_id, similar_app) VALUES (%s, %s)', (self.new_apk_id, similar_app))
		log.msg('Insert of similar apps complete! %s' % item['package_name'], level=log.INFO)
		self.connection.commit()