#!/bin/bash
clear
sudo useradd -d /home/verifiers -m verifiers
version=$(lsb_release -c -s)
sudo echo "deb http://cran.r-project.org/bin/linux/ubuntu $version/" >> "/etc/apt/sources.list"
sudo gpg --keyserver keyserver.ubuntu.com --recv-key E084DAB9
sudo gpg -a --export E084DAB9 | sudo apt-key add -
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install openjdk-7-jre openjdk-7-jdk python-scipy python-rpy2 git python-setuptools python-dev build-essential libevent-dev python-gevent language-pack-id r-cran-runit libgnustep-base-dev  gobjc gnustep gnustep-make gnustep-common ruby ant python-pip
sudo easy_install gserver
sudo easy_install tornado
export LANGUAGE=en_US.UTF-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
sudo locale-gen en_US.UTF-8
sudo dpkg-reconfigure locales
sudo mkdir /home/server
cd /home/server
sudo git clone git://github.com/SingaporeClouds/scipy-verifier.git
cp -rf /home/server/scipy-verifier/unity  /home/verifiers/unity
cp -rf /home/server/scipy-verifier/junit  /home/verifiers/junit
chmod 777 -R /home/verifiers/junit
chmod 777 -R /home/verifiers/unity
chown verifiers:verifiers -R /home/verifiers
cd scipy-verifier/installation
sudo chmod +x /home/server/scipy-verifier/installation/boot.sh
sudo ln -s /home/server/scipy-verifier/installation/boot.sh /etc/init.d/boot.sh
sudo update-rc.d boot.sh defaults


