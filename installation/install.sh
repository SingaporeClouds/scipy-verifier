#!/bin/bash
clear
sudo useradd -d /home/verifiers -m verifiers
version=$(lsb_release -c -s)
sudo echo "deb http://cran.r-project.org/bin/linux/ubuntu $version/" >> "/etc/apt/sources.list"
sudo gpg --keyserver keyserver.ubuntu.com --recv-key E084DAB9
sudo gpg -a --export E084DAB9 | sudo apt-key add -
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python-scipy python-rpy2 git python-setuptools python-dev build-essential libevent-dev python-gevent language-pack-id r-cran-runit libgnustep-base-dev  gobjc gnustep gnustep-make gnustep-common ruby
sudo easy_install gserver
export LANGUAGE=en_US.UTF-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
sudo locale-gen en_US.UTF-8
sudo dpkg-reconfigure locales
sudo mkdir /home/server
cd /home/server
sudo rm /home/server/install_r_libraries
sudo echo -e "from rpy2.robjects import r\nr(\"install.packages('testthat','/usr/lib/R/site-library/')\")" >> /home/server/install_r_libraries
sudo python /home/server/install_r_libraries
sudo git clone git://github.com/SingaporeClouds/scipy-verifier.git
cp -rf /home/server/scipy-verifier/unity  /home/verifiers/unity
chmod 777 -R /home/verifiers/unity
chown verifiers:verifiers -R /home/verifiers
cd scipy-verifier/installation
sudo cp verifiers.conf /etc/init/verifiers.conf
sudo initctl start verifiers
#echo new cron into cron fil
#sudo echo "00 03 * * * sudo /usr/bin/python /home/server/scipy-verifier/installation/update.py" >> mycron
#install new cron file
#sudo crontab mycron
#sudo rm mycron
#sudo python /home/server/scipy-verifier/installation/update.py


