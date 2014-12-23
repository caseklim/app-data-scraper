import mysql.connector as mariadb
from scrapy.exceptions import DropItem

# Inserts the APK and its related information into a MariaDB database
class MariaDBPipeline(object):

	# Opens the database connection
	def __init__(self, settings):
		self.db_info = settings.get('MARIADB_INFO')
		self.connection = mariadb.connect(user=db_info['user'], password=db_info['password'], database=db_info['database'])
		self.cursor = connection.cursor()

	# Inserts the APK, its reviews, and its similar apps into the database.
	# If an error occurs, the item is dropped. Otherwise, the APK and its
	# related information were successfully inserted into the database.
	def process_item(self, item, spider):
        try:
            self.insert_item(item)
            self.insert_reviews(item['reviews'])
            self.insert_similar_apks(item['similar_apps'])
            return item
        except mariadb.Error as e:
            raise DropItem('%s' % e.message)

    # Inserts the APK into the database
    def insert_item(self, item):
    	self.cursor.execute('INSERT INTO apk_information (package_name, name, developer, date_published, ' +
	    		'genre, description, score, num_reviews, num_one_star_reviews, num_two_star_reviews, num_three_star_reviews, ' +
	    		'num_four_star_reviews, num_five_star_reviews, whats_new, file_size, lower_installs, upper_installs, version, ' +
	    		'operating_system, content_rating) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', 
    		(item['package_name'], item['name'], item['developer'], item['date_published'], item['genre'], item['description'], 
    			item['score'], item['num_reviews'], item['num_one_star_reviews'], item['num_two_star_reviews'], item['num_three_star_reviews'],
    			item['num_four_star_reviews'], item['num_five_star_reviews'], item['whats_new'], item['file_size'], item['lower_installs'],
    			item['upper_installs'], item['version'], item['operating_system'], item['content_rating']))

    # Inserts the APK's reviews into the database
	def insert_reviews(self, reviews):
		# TODO need apk_id
		for review in reviews:
			self.cursor.execute('INSERT INTO reviews (title, body, reviewer_id, review_date, rating) VALUES (%s, %s, %s, %s, %s)',
				(review['title'], review['body'], review['reviewer_id'], review['review_date'], review['rating']))

	# Inserts the apps similar to the APK into the database
	def insert_similar_apks(self, similar_apps):
		# TODO need apk_id
		for similar_app in similar_apps:
			self.cursor.execute('INSERT INTO similar_apks (similar_apk) VALUES (%s)', (similar_app))

	return item;