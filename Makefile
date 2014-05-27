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
DAEMONANGULARNAME= singpath_angular_verifier
DAEMONUSER= verifiers

.PHONY: ./nodeserver clean deps user

./nodeserver:
	git submodule update --init

${BIN}/${DAEMONAPINAME}: ${LIB}/python_server
	ln -s ${LIB}/python_server/server.py $@
	chmod 755 $@

${BIN}/${DAEMONANGULARNAME}: ${LIB}/nodeserver
	ln -s ${LIB}/nodeserver/bin/angularjs_verifier $@
	chmod 755 $@

${LIB}:
	mkdir -p ${LIB}

${LIB}/nodeserver: ${LIB} ./nodeserver
	cp -rf ./nodeserver $@
	cd $@; npm install

${LIB}/python_server: ${LIB} ./python_server/*
	cp -rf ./python_server $@

${VAR}: user
	mkdir -p $@/logs
	chown ${DAEMONUSER}:nogroup -R $@

${VAR}/javaserver: ${VAR} ./javaserver/* ./installation/tomcat_wrapper.sh
	cp -rf ./javaserver $@
	cd $@; ant compile
	cp ./installation/tomcat_wrapper.sh $@/jsp/tomcat/bin/supervisord_wrapper.sh
	mkdir -p $@/jsp/tomcat/logs
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
	rm -rf ${BIN}/${DAEMONANGULARNAME}
	rm -rf ${VAR}
	rm -rf /etc/supervisor/conf.d/singpath.conf

deps:
	apt-get update
	apt-get upgrade -q -y
	apt-get install -q -y openjdk-7-jre openjdk-7-jdk python-scipy python-rpy2 \
		git python-setuptools python-dev build-essential libevent-dev \
		python-gevent r-cran-runit libgnustep-base-dev  gobjc gnustep \
		gnustep-make gnustep-common ruby ant python-pip curl nodejs-legacy \
		supervisor
	apt-get -q -y remove  openjdk-6-jre-lib
	cd /tmp/; wget --no-check-certificate https://www.npmjs.org/install.sh; \
		clean=yes bash install.sh; rm install.sh
	easy_install gserver
	easy_install tornado

install: install-bin install-lib install-var
	cp ./installation/supervisord.conf /etc/supervisor/conf.d/singpath.conf
	/etc/init.d/supervisor stop
	/etc/init.d/supervisor start

install-bin: ${BIN}/${DAEMONAPINAME} ${BIN}/${DAEMONANGULARNAME}

install-lib: ${LIB}/python_server ${LIB}/nodeserver

install-var: ${VAR}/javaserver ${VAR}/junit ${VAR}/nodeserver ${VAR}/unity

user:
	id ${DAEMONUSER} || adduser --system --home ${VAR} ${DAEMONUSER}
