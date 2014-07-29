#!/bin/bash
#
#

SRC=/usr/local/src/scipy-verifier

# ORIGIN=`curl http://metadata/computeMetadata/v1/project/attributes/scipy-verifier-origin -H "Metadata-Flavor: Google"`
ORIGIN="https://github.com/SingaporeClouds/scipy-verifier.git"


# COMMIT=`curl http://metadata/computeMetadata/v1/project/attributes/scipy-verifier-commit -H "Metadata-Flavor: Google"`
COMMIT="a6c4ddb587fda328e6fdc491c067df6918486c08"

function clone() {
    sudo rm -rf $SRC
    sudo git clone $ORIGIN $SRC
}

function fetch {
    cd $SRC
    sudo git fetch $ORIGIN
    cd -
}

function install() {
    cd $SRC
    sudo git checkout $COMMIT
    sudo DEBIAN_FRONTEND=noninteractive make deps install
    cd -
}

function update() {
    cd $SRC
    HEAD=`git rev-parse --verify HEAD`

    if [ "$COMMIT" != "$HEAD" ]; then
        sudo make clean
        fetch
        cd -
        install
    else
        echo "Already up-to-date"
        cd -
    fi
}

sudo apt-get update -q -y
# sudo apt-get upgrade -q -y
sudo apt-get install -q -y git
export LANGUAGE=en_US.UTF-8
export LANG=en_US.UTF-8

if [ ! -d $SRC ]; then
    echo "Installing..."
    clone
    install
else
    echo "updating..."
    update
fi
