#!/bin/bash
while read package_name
do
	( cd android_scraper_2 ; scrapy crawl apkspider -a package_name=$package_name )
done < $1