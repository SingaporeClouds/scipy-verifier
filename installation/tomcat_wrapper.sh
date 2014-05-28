#!/bin/bash
# Source: https://confluence.atlassian.com/plugins/viewsource/viewpagesrc.action?pageId=252348917
function shutdown()
{
    date
    echo "Shutting down Tomcat"
    unset CATALINA_PID # Necessary in some cases

    $TOMCAT_HOME/bin/catalina.sh stop
}

date
echo "Starting Tomcat"
export CATALINA_PID=/tmp/$$

. $TOMCAT_HOME/bin/catalina.sh start

# Allow any signal which would kill a process to stop Tomcat
trap shutdown HUP INT QUIT ABRT KILL ALRM TERM TSTP

echo "Waiting for `cat $CATALINA_PID`"
wait `cat $CATALINA_PID`
