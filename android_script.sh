#!/bin/bash
start_time=$( date +"%Y-%m-%d %T" )
while read package_name
do
	# Collect info on the app from Google Play, and then download the respective APK
	( cd android_scraper ; scrapy crawl apk -a package_name="$package_name" -a start_time="$start_time" )
	( cd google_play_crawler/googleplay ; java -jar googleplaycrawler-0.3.jar -f crawler.conf download $package_name )

	# Once the APK is downloaded, move and rename the file
	today=$( date +"%m-%d-%Y" )
	mkdir -p downloads
	mv google_play_crawler/googleplay/$package_name.apk downloads/${package_name}_${today}.apk
done < $1