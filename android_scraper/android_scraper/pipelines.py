from datetime import datetime
import mysql.connector as mariadb
import subprocess

from scrapy import log
from scrapy.exceptions import DropItem

# Inserts the APK and its related information into a MariaDB database
class MariaDBPipeline(object):

	def __init__(self, settings):
		"""
		Initializes the MariaDBPipeline.

		Args:
			settings: the Scrapy project settings
		"""
		# Maintain value(s) used across multiple functions
		self.crawling_session_id = None

		# Initialize database connection
		self.db_info = settings.get('MARIADB_INFO')
		self.connection = mariadb.connect(user=self.db_info['user'], password=self.db_info['password'], database=self.db_info['database'])
		self.cursor = self.connection.cursor()

	@classmethod
	def from_crawler(cls, crawler):
		return cls(crawler.settings)

	def process_item(self, item, spider):
		"""
		Inserts the APK, its reviews, and its similar apps into the database.
		If an error occurs, the item and its respective information is not
		inserted into the database, and the APK file is not downloaded.

		Args:
			item: the ApkItem being processed
			spider: the ApkSpider 
		"""
		try:
			# Create a new crawling session, or update the existing one
			self.create_or_update_crawling_session(item)

			# Determine whether an APK with the specified package name published on the specified date already exists in the database
			# Note: Improper practice to use the % operator with SQL queries, but practice way was always returning None
			self.cursor.execute('SELECT package_name, date_published FROM apk_information WHERE package_name="%s" AND date_published="%s"' %
				(item['package_name'], datetime.strftime(item['date_published'], '%Y-%m-%d')))
			apk = self.cursor.fetchone()

			if apk is None:
				# For a new APK or new version of an APK, insert the APK information, reviews, and similar apps into the database
				self.insert_item(item)
				self.insert_reviews(item)
				self.insert_similar_apps(item)

				# Call the Bash shell script that downloads the respective APK file
				subprocess.call('./android_script-2.sh "%s" "%s" "%s" "%s"' % (item['package_name'], 
					str(item['date_published'].year), str(item['date_published'].month), str(item['date_published'].day)), shell=True)
			else:
				# If a new version of the app has not been released since the last crawling session, only update its reviews
				self.insert_reviews(item)
		except mariadb.Error as error:
			# An error occurred with the database
			log.msg('Error: {}'.format(error), level=log.ERROR)
		except OSError as error:
			# An error occurred downloading the APK file
			log.msg('Error: {}'.format(error), level=log.ERROR)

		self.connection.close()
		return item

	def create_or_update_crawling_session(self, item):
		"""
		Creates a new crawling session or updates the current crawling session, if one is currently ongoing.

		Args:
			item: the ApkItem being processed
		"""
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
			self.cursor.execute('UPDATE android_crawling_sessions SET end_time = %s WHERE crawling_id = %s', (item['end_time'], crawling_session[0]))
			self.connection.commit()
			self.crawling_session_id = crawling_session[0]
			log.msg('Update complete!', level=log.INFO)

	def insert_item(self, item):
		"""
		Inserts the APK into the database.

		Args:
			item: the ApkItem being processed
		"""
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
		log.msg('Insert complete! %s' % item['package_name'], level=log.INFO)

	def insert_reviews(self, item):
		"""
		Inserts the APK's reviews into the database.

		Args:
			item: the ApkItem being processed
		"""
		log.msg('Inserting reviews for %s into android_reviews...' % item['package_name'], level=log.INFO)
		for review in item['reviews']:
			# Catch the error here to avoid insertion of duplicate reviews, but to allow the insertion of new reviews
			try:
				self.cursor.execute('INSERT INTO android_reviews (package_name, date_published, title, body, reviewer_id, review_date, rating) VALUES (%s, %s, %s, %s, %s, %s, %s)',
					(item['package_name'], item['date_published'], review['title'], review['body'], review['reviewer_id'], review['review_date'], review['rating']))
			except mariadb.Error as error:
				log.msg('Error: {}'.format(error), level=log.ERROR)
		log.msg('Insert of reviews complete! %s' % item['package_name'], level=log.INFO)
		self.connection.commit()

	def insert_similar_apps(self, item):
		"""
		Inserts the apps similar to the APK into the database

		Args:
			item: the ApkItem being processed
		"""
		log.msg('Inserting similar apps for %s into similar_android_apps...' % item['package_name'], level=log.INFO)
		for similar_app in item['similar_apps']:
			self.cursor.execute('INSERT INTO similar_android_apps (package_name, date_published, similar_app) VALUES (%s, %s, %s)', 
				(item['package_name'], item['date_published'], similar_app))
		log.msg('Insert of similar apps complete! %s' % item['package_name'], level=log.INFO)
		self.connection.commit()
