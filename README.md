android-scraper-2
=================
## Commands
./android_script.sh apk_list.txt

scrapy crawl googleplay -a file_name=apk_list.txt

## Dependencies
Before installing any of the following dependencies, update the package index:
```
sudo apt-get update
```

**pip**
```
sudo apt-get install python-pip
```

**Python Requests library**
```
pip install requests
```

**Python MySQL Connector**
```
sudo pip install mysql-connector-python --allow-external mysql-connector-python
```

**Scrapy**
```
pip install Scrapy
```

**Java**
```
sudo apt-get install openjdk-6-jre
sudo apt-get install default-jre
```

**Google Protocol Buffers**
```
sudo apt-get install protobuf-compiler libprotobuf-java
```

**sbt**
```
sudo apt-get remove scala-library scala
wget http://www.scala-lang.org/files/archive/scala-2.11.4.deb
sudo dpkg -i scala-2.11.4.deb
sudo apt-get update
sudo apt-get install scala

wget http://dl.bintray.com/sbt/debian/sbt-0.13.6.deb
sudo dpkg -i sbt-0.13.6.deb 
sudo apt-get update
sudo apt-get install sbt
```

**MariaDB**

Instructions from here:  
https://mariadb.com/kb/en/mariadb/documentation/getting-started/binary-packages/installing-mariadb-deb-files
```
sudo apt-key adv --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 0xcbcb082a1bb943db

sudo apt-get install software-properties-common 
sudo apt-key adv --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 0xcbcb082a1bb943db 
sudo add-apt-repository 'deb http://ftp.osuosl.org/pub/mariadb/repo/10.0/ubuntu trusty main'

sudo apt-get install mariadb-server
```