#scipy-verifier

The SciPy verifier for SingPath


## setup

ssh to a fresh instance with a backport debian 7 image:
```
sudo apt-get install git
cd /tmp/
git clone git://github.com/SingaporeClouds/scipy-verifier.git
cd scipy-verifier
sudo make deps
export LANGUAGE=en_US.UTF-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
sudo locale-gen en_US.UTF-8
sudo dpkg-reconfigure locales
sudo make install
```