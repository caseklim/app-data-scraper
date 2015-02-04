from scrapy.item import Item, Field

class ItunesItem(Item):
	id							= Field() # Unique identifier
	bundle_id					= Field() # Bundle identifier
	name						= Field() # Name of the app
	developer					= Field() # Developer that published the app
	price						= Field() # How much the app costs
	description					= Field() # Description of the app
	release_notes				= Field() # Description of new features in the current version
	genre						= Field() # Category (e.g. Books)
	release_date				= Field() # Date the app was originally released on iTunes
	updated_date				= Field() # Date the latest version of the app was released
	version						= Field() # Current version
	file_size					= Field() # File size
	content_advisory_rating		= Field() # Maturity (e.g. 4+)
	rating_current_version		= Field() # Average customer rating of the current version
	num_ratings_current_version	= Field() # Rating count for the current version
	rating_all_versions			= Field() # Average customer rating of all versions
	num_ratings_all_versions	= Field() # Rating count for all versions
	customer_reviews			= Field() # Reviews for the current version of the app
	minimum_os_version			= Field() # Minimum OS required to suppor the app

	start_time              	= Field() # The time at which scraping began for this Item
	end_time                	= Field() # The time at which scraping ended for this Item