from datetime import datetime
import mysql.connector as mariadb

from scrapy import log
from scrapy.exceptions import DropItem

# Inserts the iOS app and its related information into a MariaDB database
class MariaDBPipeline(object):

	def __init__(self, settings):
		# Maintain value(s) used across multiple functions
		self.crawling_session_id = None

		# Initialize database connection
		self.db_info = settings.get('MARIADB_INFO')
		self.connection = mariadb.connect(user=self.db_info['user'], password=self.db_info['password'], database=self.db_info['database'])
		self.cursor = self.connection.cursor()

	@classmethod
	def from_crawler(cls, crawler):
		return cls(crawler.settings)

	# Inserts the app, its reviews, and its similar apps into the database.
	# If an error occurs, the item and its respective information is not
	# inserted into the database.
	def process_item(self, item, spider):
		try:
			# Create a new crawling session, or update the existing one
			self.create_or_update_crawling_session(item)

			# Determine whether an app with the specified ID published on the specified date already exists in the database
			# Note: Improper practice to use the % operator with SQL queries, but practice way was always returning None
			self.cursor.execute('SELECT id, updated_date FROM ios_app_information WHERE id="%s" AND updated_date="%s"' %
				(item['id'], datetime.strftime(item['updated_date'], '%Y-%m-%d')))
			app = self.cursor.fetchone()

			if app is None:
				# For a new app or new version of an app, insert the app information and reviews into the database
				self.insert_item(item)
				self.insert_reviews(item)
			else:
				# If a new version of the app has not been released since the last crawling session, only update its reviews
				self.insert_reviews(item)
		except mariadb.Error as error:
			log.msg('Error: {}'.format(error), level=log.ERROR)

		self.connection.close()
		return item

	# Creates a new crawling session or updates the current
	# crawling session, if one is currently ongoing.
	def create_or_update_crawling_session(self, item):
		self.cursor.execute('SELECT crawling_id, start_time FROM ios_crawling_sessions ORDER BY start_time DESC LIMIT 1')
		crawling_session = self.cursor.fetchone()

		if crawling_session is None or (crawling_session is not None and crawling_session[1].strftime('%Y-%m-%d %H:%M:%S') != item['start_time']):
			# If no crawling sessions exist or this is the start of a new crawling 
			# session (i.e. the start time of the last row is not equal to the start 
			# time for the current item), then create a new crawling session.
			log.msg('Creating new crawling session with start time %s...' % item['start_time'], level=log.INFO)
			self.cursor.execute('INSERT INTO ios_crawling_sessions (start_time, end_time) VALUES (%s, %s)', (item['start_time'], item['end_time']))
			self.connection.commit()
			self.crawling_session_id = self.cursor.lastrowid
			log.msg('Creation complete! crawling_id = %s' % self.crawling_session_id)
		else:
			# Otherwise, update the current crawling session with the latest end time.
			log.msg('Updating crawling session %s with end time %s...' % (crawling_session[0], item['end_time']), level=log.INFO)
			self.cursor.execute('UPDATE ios_crawling_sessions SET end_time = %s WHERE crawling_id = %s', (item['end_time'], crawling_session[0]))
			self.connection.commit()
			self.crawling_session_id = crawling_session[0]
			log.msg('Update complete!', level=log.INFO)

	# Inserts the APK into the database
	def insert_item(self, item):
		log.msg('Inserting %s into ios_app_information...' % item['id'], level=log.INFO)
		self.cursor.execute('INSERT INTO ios_app_information (id, bundle_id, name, developer, ' +
				'price, description, release_notes, genre, release_date, updated_date, version, ' +
				'file_size, content_advisory_rating, rating_current_version, num_ratings_current_version, ' +
				'rating_all_versions, num_ratings_all_versions, minimum_os_version, crawling_session_id) ' +
				'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', 
			(item['id'], item['bundle_id'], item['name'], item['developer'], item['price'], item['description'], 
				item['release_notes'], item['genre'], item['release_date'], item['updated_date'], item['version'],
				item['file_size'], item['content_advisory_rating'], item['rating_current_version'], item['num_ratings_current_version'],
				item['rating_all_versions'], item['num_ratings_all_versions'], item['minimum_os_version'], self.crawling_session_id))
		self.connection.commit()
		log.msg('Insert complete! %s' % item['id'], level=log.INFO)

	# Inserts the app's reviews into the database
	def insert_reviews(self, item):
		log.msg('Inserting reviews for %s into ios_reviews...' % item['id'], level=log.INFO)
		for review in item['customer_reviews']:
			# Catch the error here to avoid insertion of duplicate reviews, but to allow the insertion of new reviews
			try:
				self.cursor.execute('INSERT INTO ios_reviews (app_id, updated_date, topic, rating, user, review, version) VALUES (%s, %s, %s, %s, %s, %s, %s)',
					(item['id'], item['updated_date'], review['topic'], review['rating'], review['user'], review['review'], review['version']))
			except mariadb.Error as error:
				log.msg('Error: {}'.format(error), level=log.ERROR)
		log.msg('Insert of reviews complete! %s' % item['id'], level=log.INFO)
		self.connection.commit()
