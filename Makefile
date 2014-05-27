# Install the api and verifier servers in:
#
#  - /user/local/lib/singpath_verifier
#  - /user/local/bin
#  - /var/local/singpath_verifier
#
#  It also create a system user with its home /var/local/singpath_verifier
#

PREFIX= /usr/local
BIN= ${PREFIX}/bin
LIB= ${PREFIX}/lib/singpath_verifier
VAR= /var/local/singpath_verifier
DAEMONAPINAME= singpath_verifier_api
DAEMONUSER= verifiers

.PHONY: ./nodeserver clean deps user

./nodeserver:
	git submodule update --init

${BIN}/${DAEMONAPINAME}: ${LIB}/python_server
	ln -s ${LIB}/python_server/server.py ${BIN}/${DAEMONAPINAME}
	chmod 755 ${BIN}/${DAEMONAPINAME}

${LIB}:
	mkdir -p ${LIB}

${LIB}/bin: ${LIB} ./bin/*
	cp -rf ./bin $@

${LIB}/nodeserver: ${LIB} ./nodeserver
	cp -rf ./nodeserver $@
	cd $@; npm install

${LIB}/python_server: ${LIB} ./python_server/*
	cp -rf ./python_server $@

${VAR}: user
	mkdir -p $@
	chown ${DAEMONUSER}:nogroup -R $@

${VAR}/javaserver: ${VAR} ./javaserver/*
	cp -rf ./javaserver $@
	cd $@; ant compile
	chmod 755 -R $@
	chown ${DAEMONUSER}:nogroup -R $@

${VAR}/unity: ${VAR} ./python_server/unity/*
	cp -rf ./python_server/unity $@
	chmod 755 -R $@
	chown ${DAEMONUSER}:nogroup -R $@

${VAR}/junit: ${VAR} ./python_server/junit/*
	cp -rf ./python_server/junit $@
	chmod 755 -R $@
	chown ${DAEMONUSER}:nogroup -R $@

${VAR}/nodeserver:
	mkdir -p $@
	chmod 755 -R $@
	chown ${DAEMONUSER}:nogroup -R $@

clean:
	rm -rf ${LIB}
	rm -rf ${BIN}/${DAEMONAPINAME}
	rm -rf ${VAR}

deps:
	apt-get update
	apt-get upgrade
	apt-get install openjdk-7-jre openjdk-7-jdk python-scipy python-rpy2 git python-setuptools python-dev build-essential libevent-dev python-gevent r-cran-runit libgnustep-base-dev  gobjc gnustep gnustep-make gnustep-common ruby ant python-pip curl nodejs-legacy
	cd /tmp/; wget --no-check-certificate https://www.npmjs.org/install.sh; bash install.sh
	sudo easy_install gserver
	sudo easy_install tornado

install: install-bin install-lib install-var

install-bin: ${BIN}/${DAEMONAPINAME}

install-lib: ${LIB}/python_server ${LIB}/nodeserver ${LIB}/bin

install-var: ${VAR}/javaserver ${VAR}/junit ${VAR}/nodeserver ${VAR}/unity

user:
	id ${DAEMONUSER} || adduser --system --home ${VAR} ${DAEMONUSER}
