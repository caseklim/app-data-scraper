from scrapy.item import Item, Field

class ItunesItem(Item):
	id							= Field() # Unique identifier
	name						= Field() # Name of the app
	developer					= Field() # Developer that published the app
	description					= Field() # Description of the app
	whats_new					= Field() # Description of new features in the current version
	category					= Field() # Category (e.g. Books)
	release_date				= Field() # Date the app was released to iTunes
	version						= Field() # Current version
	file_size					= Field() # File size
	languages					= Field() # Languages supported by the app
	rating						= Field() # Maturity (e.g. 4+)
	requirements				= Field() # Device compatibility
	rating_current_version		= Field() # Average customer rating of the current version
	num_ratings_current_version	= Field() # Rating count for the current version
	rating_all_versions			= Field() # Average customer rating of all versions
	num_ratings_all_versions	= Field() # Rating count for all versions
	customer_reviews			= Field() # Reviews for the current version of the app

	start_time              	= Field() # The time at which scraping began for this Item
	end_time                	= Field() # The time at which scraping ended for this Item