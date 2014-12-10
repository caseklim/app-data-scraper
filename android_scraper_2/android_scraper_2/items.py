from scrapy.item import Item, Field

class ApkItem(Item):
    package_name            = Field() # Unique package name
    name                    = Field() # Name of the app
    developer               = Field() # Developer that published the app
    date_published          = Field() # Date the app was published to Google Play
    genre                   = Field() # Genre (e.g. Social)
    description             = Field() # Description of the app
    score                   = Field() # Average rating
    num_reviews             = Field() # Total number of reviews
    num_one_star_reviews    = Field() # Number of one-star reviews
    num_two_star_reviews    = Field() # Number of two-star reviews
    num_three_star_reviews  = Field() # Number of three-star reviews
    num_four_star_reviews   = Field() # Number of four-star reviews
    num_five_star_reviews   = Field() # Number of five-star reviews
    whats_new               = Field() # Description of new features in the current version
    file_size               = Field() # File size
    lower_installs          = Field() # Number of installs on the lower end
    upper_installs          = Field() # Number of installs on the upper end
    version                 = Field() # Current version
    operating_system        = Field() # Version of Android the app is compatible with
    content_rating          = Field() # Maturity (e.g. Medium Maturity)
    reviews                 = Field() # Reviews for the current version of the app
    similar_apps            = Field() # Apps listed as similar to the app