from gevent.monkey import patch_all
patch_all()

from tornado.options import define, options, parse_command_line, print_help

define("config", default='debug', help="run configuration settings", type=str)
define("local_settings", default="true", help="enable/disable use of local settings", type=str)
from features.configuration import Configuration
parse_command_line()
Configuration.initialize()



import features.logging as sms_api_logger

payment_log = sms_api_logger.PaymentLogger()


scart_log = sms_api_logger.SCartLogger()

general_log = sms_api_logger.GeneralLogger()


payment_log.info( 'payment sequence start', {'amount': 500, 'cid':1} )
payment_log.error( 'payment sequence error!', {'amount': 500, 'cid':1} )
payment_log.debug( 'payment sequence debug!', {'amount': 500, 'cid':1} )



# general_log.info( 'general sequence start', {'amount': 500, 'cid':1} )
# general_log.error( 'general sequence error!', {'amount': 500, 'cid':1} )
# general_log.debug( 'general sequence debug!', {'amount': 500, 'cid':1} )
# 
# 
# scart_log.info( 'scart sequence start', {'amount': 500, 'cid':1} )
# scart_log.error( 'scart sequence error!', {'amount': 500, 'cid':1} )
# scart_log.debug( 'scart sequence debug!', {'amount': 500, 'cid':1} )



#from utils import fluent_logging

# content= {'msg':'msg, msg, msg', 'data':'data data data'}
# 
# 
# fluent_logging.fluent_send( f_sender=fluent_logging.f_general_sender, tag='INFO', content=content )
# fluent_logging.fluent_send( f_sender=fluent_logging.f_shopping_cart_sender, tag='INFO', content=content )
# fluent_logging.fluent_send( f_sender=fluent_logging.f_payment_sender, tag='INFO', content=content )
# 
# fluent_logging.fluent_send( f_sender=fluent_logging.f_general_sender, tag='ERROR', content=content )
# fluent_logging.fluent_send( f_sender=fluent_logging.f_shopping_cart_sender, tag='ERROR', content=content )
# fluent_logging.fluent_send( f_sender=fluent_logging.f_payment_sender, tag='ERROR', content=content )
# 
# fluent_logging.fluent_send( f_sender=fluent_logging.f_general_sender, tag='DEBUG', content=content )
# fluent_logging.fluent_send( f_sender=fluent_logging.f_shopping_cart_sender, tag='DEBUG', content=content )
# fluent_logging.fluent_send( f_sender=fluent_logging.f_payment_sender, tag='DEBUG', content=content )

