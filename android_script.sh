#!/bin/bash
while read package_name
do
	( cd android_scraper_2 ; scrapy crawl apkspider -a package_name=$package_name )
	( cd google-play-crawler/googleplay ; java -jar googleplaycrawler-0.3.jar -f crawler.conf download $package_name)
done < $1