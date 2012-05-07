#!/bin/bash
clear
sudo useradd -d /home/verifiers -m verifiers
sudo echo "\ndeb http://cran.r-project.org/bin/linux/ubuntu oneiric/" >> "/etc/apt/sources.list"
sudo gpg --keyserver keyserver.ubuntu.com --recv-key E084DAB9
sudo gpg -a --export E084DAB9 | sudo apt-key add -
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python-scipy python-rpy2 git python-setuptools python-dev build-essential libevent-dev python-gevent
sudo easy_install gserver
sudo mkdir /home/server
cd /home/server
sudo mkdir libs
sudo echo "from rpy2.robjects import r\nr(\"install.packages('testthat','/home/server/libs')\")\nr(\"install.packages('RUnit','/home/server/libs')\")" >> install_r_libraries
sudo python install_r_libraries
sudo git clone git://github.com/SingaporeClouds/scipy-verifier.git
cd scipy-verifier/installation
sudo cp verifiers.conf /etc/init/verifiers.conf
initctl start verifiers
initctl status verifiers



