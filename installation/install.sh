#!/bin/bash
clear
sudo useradd -d /home/verifiers -m verifiers
sudo echo "deb http://ftp.us.debian.org/debian wheezy-backports main" >> "/etc/apt/sources.list"
version=$(lsb_release -c -s)
sudo echo "deb http://cran.r-project.org/bin/linux/ubuntu $version/" >> "/etc/apt/sources.list"
sudo gpg --keyserver keyserver.ubuntu.com --recv-key E084DAB9
sudo gpg -a --export E084DAB9 | sudo apt-key add -
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install openjdk-7-jre openjdk-7-jdk python-scipy python-rpy2 git python-setuptools python-dev build-essential libevent-dev python-gevent language-pack-id r-cran-runit libgnustep-base-dev  gobjc gnustep gnustep-make gnustep-common ruby ant python-pip curl nodejs-legacy
curl --insecure https://www.npmjs.org/install.sh | bash
sudo npm install -g grunt-cli
sudo easy_install gserver
sudo easy_install tornado
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
cd /home/server/scipy-verifier/
sudo git submodule update --init
cd /home/server/scipy-verifier/nodeserver
npm install
cd /home/server
cp -rf /home/server/scipy-verifier/unity  /home/verifiers/unity
cp -rf /home/server/scipy-verifier/junit  /home/verifiers/junit
mkdir /home/verifiers/nodeserver
chmod 777 -R /home/verifiers/junit
chmod 777 -R /home/verifiers/unity
chmod 777 -R /home/verifiers/nodeserver
chown verifiers:verifiers -R /home/verifiers
cd scipy-verifier/installation
sudo python /home/server/scipy-verifier/installation/cran.py
sudo chmod +x /home/server/scipy-verifier/installation/boot.sh
sudo ln -s /home/server/scipy-verifier/installation/boot.sh /etc/init.d/boot.sh
sudo update-rc.d boot.sh defaults


