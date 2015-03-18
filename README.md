app-data-scraper
=================
#1 Dependencies
The following utilities are required for various aspects of the project:

* [Python 2.7](https://www.python.org/download/releases/2.7/)
* [Python Requests library](http://docs.python-requests.org/en/latest/)
* [Python MySQL Connector](https://pypi.python.org/pypi/MySQL-python)
* Python ElementTree
* [Scrapy](http://scrapy.org)
* Java
* [Google Protocol Buffers](https://developers.google.com/protocol-buffers/)
* [sbt](http://www.scala-sbt.org/release/tutorial/Setup.html)
* [MariaDB](https://mariadb.com)

#2 Android / Google Play
The /android_scraper directory contains a Scrapy project that is used to crawl Google Play and collect information on Android apps.

##2.1 ```GooglePlaySpider```
The file google\_play_spider.py defines a Scrapy spider that is used to traverse Google Play and create a .txt file containing a list of Android package names, which is then used by ```ApkSpider```.

**Note:** This file was adapted from [here](https://github.com/anderson916/google-play-crawler). Although it was functional at one time, I believe it is no longer functional now.

The spider can be started as follows:

```scrapy crawl googleplay -a file_name=apk_list.txt```

Where apk_list.txt is the name of the file in which to create the list of Android package names.

**Note:** In settings.py, ```android_scraper.pipelines.MariaDBPipeline``` should be set to ```None``` when using this spider.

##2.2 ```ApkSpider```
The file apk_spider.py defines a Scrapy spider that is used to collect information on a single Android app, and download the respective APK file.

The spider can be started as follows:

```scrapy crawl apk -a package_name=package.name```

Where package.name is the respective package name (e.g. com.facebook.katana for Facebook) of the app to collect information on.

The file pipelines.py uses the MariaDB database to determine whether information has been collected on the current version of the app. If the app's information has not been previously collected, or a new version of the app has been released, then the app's information is inserted into the database (including user reviews), and the respective APK file is downloaded. If no new version of the app has been released since the previous crawling session, then only new user reviews are inserted into the database (if any), and the respective APK file is not downloaded.

##2.3 Shell Scripts
Inside this project, there are two script files: android\_script.sh and android_script-2.sh.

###2.3.1 android_script.sh
This file is the "master" script used to start the scraper. This script is used as follows:

```./android_script.sh apk_list.txt```

Where apk_list.txt is a text file containing a list of Android package names.

For each package name in the file, the script executes ```ApkSpider``` with that package name.

###2.3.2 android_script-2.sh
This script is called from within pipelines.py, after the app information has been inserted into the MariaDB database.

The Google Play API is used to first download the respective APK file, and the script then moves and renames that file.

This script is designed to work within the server, as APK files are moved into the /conflux/Android directory.

APK files are named in the format of package.name-YYYY\_M_D.apk (e.g. Facebook published on 3/12/15 would be saved as the following file: com.facebook.katana-2015\_3\_12.apk).

#3 iOS / iTunes
The /itunes_scraper directory contains a Scrapy project that is used to crawl iTunes and collect information on iOS apps.

##3.1 ```ITunesSpider```
The file itunes_spider.py defines a Scrapy spider that is used to traverse iTunes and create a .txt file containing a list of iOS app IDs, which is then used by ```IosSpider```.

**Note:** I don't believe this file works fully as intended. My guess is that it should be implemented using ```Rule``` and ```SgmlLinkExtractor``` similarly to ```GooglePlaySpider```.

The spider can be started as follows:

```scrapy crawl itunes -a file_name=ios_list.txt```

Where ios_list.txt is the name of the file in which to create the list of iOS app IDs.

**Note:** In settings.py, ```android_scraper.pipelines.MariaDBPipeline``` should be set to ```None``` when using this spider.

##3.2 ```IosSpider```
The file ios_spider.py defines a Scrapy spider that is used to collect information on a single iOS app.

The spider can be started as follows:

```scrapy crawl ios -a app_id=#########```

Where ######### is the respective 9-digit identifier for the app to collect information on.

The file pipelines.py uses the MariaDB database to determine whether information has been collected on the current version of the app. If the app's information has not been previously collected, or a new version of the app has been released, then the app's information is inserted into the database (including user reviews). If no new version of the app has been released since the previous crawling session, then only new user reviews are inserted into the database (if any).

##3.3 Shell Script
This file is the "master" script used to start the scraper. This script is used as follows:

```./ios_script.sh ios_list.txt```

Where ios_list.txt is a text file containing a list of iOS app IDs.

For each ID in the file, the script executes ```IosSpider``` with that app ID.

#4 Server Information
The current location of the server is vm-017.main.ad.rit.edu, which is configured with Red Hat Enterprise Linux 6.

/conflux is the shared space that is used for the APK files, among other things. Files should not be moved into this space. Files need to be created or copied into this space or permissions will not be correct.

There is a file called .my.cnf that is in your home directory. This file contains the necessary login information to talk to the MariaDB instance. Just type ```mysql``` on the command line and it will automatically log you in to MariaDB and connect you to the correct database.

You have the ability to install any python modules you wish using pip and the following syntax: 

```pip install --user scrapy```

Python modules you install with the ```--user``` designation will end up in your $HOME/.local directory.  $HOME/.local/bin is already in your $PATH by default in RHEL 6, so there is nothing else to configure.

#5 Additional References
* [Scrapy 0.24 documentation](http://doc.scrapy.org/en/0.24)
* [google-play-crawler by Akdeniz on GitHub](https://github.com/Akdeniz/google-play-crawler)
* [AppStoreReviews by grych on GitHub](https://github.com/grych/AppStoreReviews)