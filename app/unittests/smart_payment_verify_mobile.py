from tornado.options import define, parse_command_line
from features.configuration import Configuration


import gevent
import gredis.client

import unittest

define("config", default='debug', help="run configuration settings", type=str)
define("local_settings", default="true", help="enable/disable use of local settings", type=str)

parse_command_line()
Configuration.initialize()


values = Configuration.values()

import gevent
from gevent.pool import Pool


from features.shopping_cart.shopping_cart import process_smart_payment_verification



job_pool = Pool( 20 )


def job():


    account_id=4
    
    pincode='43H3JW'
    checkout_id=225
    
    try:
        process_smart_payment_verification( account_id, pincode, checkout_id )
    
    except Exception, e:
        print 'exception raised: %s' % e
    
#job()

events = []
events.append( gevent.spawn( job  ) )
events.append( gevent.spawn( job  ) )
 
 
#job_pool.spawn( job  )
print 'join'
 
 
 
 
gevent.joinall( events )