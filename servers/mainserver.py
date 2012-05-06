'''
Created on 05/05/2012

@author: cristian
'''

import re
import json
import logging
import doctest
import traceback
import time
import subprocess
import os
import signal


from gevent import Greenlet
from gserver.routes import Routes
from gserver.request import parse_vals
from gserver.wsgi import WSGIServer
from gevent import monkey
monkey.patch_all()
from Queue import Empty,Queue
from scipyverifier import runScipyInstance,TimeoutException
from threading import Thread

type=0#0 accept reuqest, no accept


#R page handler
@route("^/R_test$")
def RPage(req):
    return [R_page_htm]