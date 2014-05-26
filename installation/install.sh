#!/bin/bash
sudo apt-get install git
cd /tmp/
git clone git://github.com/SingaporeClouds/scipy-verifier.git
cd scipy-verifier
sudo make deps
sudo make install
export LANGUAGE=en_US.UTF-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
sudo locale-gen en_US.UTF-8
sudo dpkg-reconfigure locales
# TODO:
#
# sudo echo -e "from rpy2.robjects import r\nr(\"install.packages('testthat','/usr/lib/R/site-library/')\")" >> /home/server/install_r_libraries
# sudo python /home/server/install_r_libraries
# sudo chmod +x /home/server/scipy-verifier/installation/boot.sh
# sudo ln -s /home/server/scipy-verifier/installation/boot.sh /etc/init.d/boot.sh
# sudo update-rc.d boot.sh defaults
