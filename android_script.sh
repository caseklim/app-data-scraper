#!/bin/bash
start_time=$( date +"%Y-%m-%d %T" )
while read package_name
do
	# Collect info on the app from Google Play, and then download the respective APK from inside the scraper
	( cd android_scraper ; scrapy crawl apk -a package_name="$package_name" -a start_time="$start_time" )
done < $1