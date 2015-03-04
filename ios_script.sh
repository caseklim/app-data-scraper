#!/bin/bash
start_time=$( date +"%Y-%m-%d %T" )
while read app_id
do
	# Collect info on the app from the App Store
	( cd itunes_scraper ; scrapy crawl ios -a app_id="$app_id" -a start_time="$start_time" )
done < $1
