'''
@author: vincent agudelo

this is an offline application that constantly reads database and executes
payment based on saved token



### WARNING ###

DO NOT USE THIS FILE DIRECTLY. INSTALL THIS SOMEWHERE IN THE ROOT OF THE APP
SAME AS GCONNECT.PH

###############

'''
from gevent.monkey import patch_all
patch_all()

from gtornado.httpclient import patch_tornado_httpclient
patch_tornado_httpclient()

import gevent
from tornado.options import define, options, parse_command_line
from features.configuration import Configuration





define("config", default='debug', help="run configuration settings", type=str)
define("local_settings", default="true", help="enable/disable use of local settings", type=str)
# time (in seconds) before executing next query


parse_command_line()
Configuration.initialize()

from features.paypal.paypal_main import run_payment


def  main():

    run_payment()
    


gevent.spawn(main).join()