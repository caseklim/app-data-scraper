from datetime import datetime
import mysql.connector as mariadb

from scrapy import log
from scrapy.exceptions import DropItem

# Inserts the APK and its related information into a MariaDB database
class MariaDBPipeline(object):

	def __init__(self, settings):
		# Maintain values used across multiple functions
		self.new_apk_id = None
		self.crawling_session_id = None

		# Initialize database connection
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
			self.create_or_update_crawling_session(item)
			self.insert_item(item)
			self.insert_reviews(item)
			self.insert_similar_apps(item)
		except mariadb.Error as error:
			log.msg('Error: {}'.format(error), level=log.ERROR)
		finally:
			self.connection.close()
			return item

	# Creates a new crawling session or updates the current
	# crawling session, if one is currently ongoing.
	def create_or_update_crawling_session(self, item):
		self.cursor.execute('SELECT crawling_id, start_time FROM android_crawling_sessions ORDER BY start_time DESC LIMIT 1')
		crawling_session = self.cursor.fetchone()

		if crawling_session is None or (crawling_session is not None and crawling_session[1].strftime('%Y-%m-%d %H:%M:%S') != item['start_time']):
			# If no crawling sessions exist or this is the start of a new crawling 
			# session (i.e. the start time of the last row is not equal to the start 
			# time for the current item), then create a new crawling session.
			log.msg('Creating new crawling session with start time %s...' % item['start_time'], level=log.INFO)
			self.cursor.execute('INSERT INTO android_crawling_sessions (start_time, end_time) VALUES (%s, %s)', (item['start_time'], item['end_time']))
			self.connection.commit()
			self.crawling_session_id = self.cursor.lastrowid
			log.msg('Creation complete! crawling_id = %s' % self.crawling_session_id)
		else:
			# Otherwise, update the current crawling session with the latest end time.
			log.msg('Updating crawling session %s with end time %s...' % (crawling_session[0], item['end_time']), level=log.INFO)
			self.cursor.execute('UPDATE crawling_sessions SET end_time = %s WHERE crawling_id = %s', (item['end_time'], crawling_session[0]))
			self.connection.commit()
			self.crawling_session_id = crawling_session[0]
			log.msg('Update complete!', level=log.INFO)

	# Inserts the APK into the database
	def insert_item(self, item):
		log.msg('Inserting %s into apk_information...' % item['package_name'], level=log.INFO)
		self.cursor.execute('INSERT INTO apk_information (package_name, name, developer, date_published, ' +
				'genre, description, score, num_reviews, num_one_star_reviews, num_two_star_reviews, num_three_star_reviews, ' +
				'num_four_star_reviews, num_five_star_reviews, whats_new, file_size, lower_installs, upper_installs, version, ' +
				'operating_system, content_rating, crawling_session_id) ' +
				'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', 
			(item['package_name'], item['name'], item['developer'], item['date_published'], item['genre'], item['description'], 
				item['score'], item['num_reviews'], item['num_one_star_reviews'], item['num_two_star_reviews'], item['num_three_star_reviews'],
				item['num_four_star_reviews'], item['num_five_star_reviews'], item['whats_new'], item['file_size'], item['lower_installs'],
				item['upper_installs'], item['version'], item['operating_system'], item['content_rating'], self.crawling_session_id))
		self.connection.commit()
		self.new_apk_id = self.cursor.lastrowid
		log.msg('Insert complete! %s' % item['package_name'], level=log.INFO)

	# Inserts the APK's reviews into the database
	def insert_reviews(self, item):
		log.msg('Inserting reviews for %s into android_reviews...' % item['package_name'], level=log.INFO)
		for review in item['reviews']:
			self.cursor.execute('INSERT INTO android_reviews (apk_id, title, body, reviewer_id, review_date, rating) VALUES (%s, %s, %s, %s, %s, %s)',
				(self.new_apk_id, review['title'], review['body'], review['reviewer_id'], review['review_date'], review['rating']))
		log.msg('Insert of reviews complete! %s' % item['package_name'], level=log.INFO)
		self.connection.commit()

	# Inserts the apps similar to the APK into the database
	def insert_similar_apps(self, item):
		log.msg('Inserting similar apps for %s into similar_android_apps...' % item['package_name'], level=log.INFO)
		for similar_app in item['similar_apps']:
			self.cursor.execute('INSERT INTO similar_android_apps (apk_id, similar_app) VALUES (%s, %s)', (self.new_apk_id, similar_app))
		log.msg('Insert of similar apps complete! %s' % item['package_name'], level=log.INFO)
		self.connection.commit()
