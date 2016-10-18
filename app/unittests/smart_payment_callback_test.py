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


import features.payments.checkout as checkout_payment
from features.payments.checkout import __process_on_payment_success

import features.logging as sms_api_logger


l = sms_api_logger.PaymentLogger()

checkout_id=226
account_id=4

__process_on_payment_success(checkout_id=checkout_id, 
                             account_id=account_id, 
                             good_response=True, l=l)


# checkout_payment.on_payment_success(  callback_response = callback_response_body,    
#                                       checkout_id=params_dict['checkout_id'], 
#                                       account_id=params_dict['account_id'] )