( cd ../google-play-crawler/googleplay ; java -jar googleplaycrawler-0.3.jar -f crawler.conf download $1 )

# Once the APK is downloaded, move and rename the file to the following format: package.name-YYY_MM_DD.apk where YYYY_MM_DD is the date on which it was updated
mkdir -p downloads
mv ../google-play-crawler/googleplay/$1.apk ../../Android/${1}-${2}_${3}_${4}.apk