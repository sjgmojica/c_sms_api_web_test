'''
checkout payment listener

usage
  python payment_queue_listener --config=debug --local_settings=true


listens to queue and brpop's the checkout id's to process

@author: vincent agudelo

'''

from gevent.monkey import patch_all
patch_all()

import gredis.client
from tornado.options import define, options, parse_command_line, print_help

define("config", default='debug', help="run configuration settings", type=str) 
define("local_settings", default="true", help="enable/disable use of local settings", type=str)

from features.configuration import Configuration

# load config FIRST
parse_command_line()
Configuration.initialize()


import features.payments.payment as payment_tool

import features.logging as sms_api_logger

values = Configuration.values()

redisconn = gredis.client.Connection(  address=str(values['redis_servers']['sms_api']['host']), port=int(values['redis_servers']['sms_api']['port']))
redisconn.connect()

payment_queue_key =  values['checkout_queue_key']


class InvalidCheckoutIdFormat( Exception ):
    pass

while True : 
    try :
        result = redisconn.brpop( payment_queue_key )
        payment_logger = sms_api_logger.PaymentLogger()
        
        payment_logger.info('pop payment from [%s]'%payment_queue_key, result)
        
        # format of result should be like
        # cid:%s
        # i.e. cid:123
        try :
            checkout_id = int(result[1].split(':')[1])
            success = payment_tool.pay_via_smart_payment( checkout_id )
            payment_logger.info('payment sequence done')
            if success :
                payment_logger.info('payment successful', result)
            else:
                payment_logger.error('payment failure', result)
            
            
        except Exception,e:
            raise InvalidCheckoutIdFormat('invalid input %s ; %s' % (e ,result) )
            
        
    except InvalidCheckoutIdFormat, e :
        payment_logger.error('will not process', e)
        
    except Exception , e:
        payment_logger.error( 'exception raised', e )