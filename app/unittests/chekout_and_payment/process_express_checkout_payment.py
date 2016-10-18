from gevent.monkey import patch_all
patch_all()
from tornado.options import define, options, parse_command_line, print_help
from features.configuration import Configuration

from gtornado.httpclient import patch_tornado_httpclient
patch_tornado_httpclient()

define("config", default='debug', help="run configuration settings", type=str)
define("local_settings", default="true", help="enable/disable use of local settings", type=str)

from datetime import datetime


if __name__ == '__main__':


    parse_command_line()
    Configuration.initialize()
    
    values = Configuration.values()
    
    
    from features.paypal import paypal_main
    from features.paypal import paypal_api_tools
    
    from features.paypal.paypal_token_model import PaypalToken
    
    
    
    pending_token = PaypalToken( token_string='hehehe7e7e7e7e7e',
                     date_created = datetime.now(),
                     checkout_id = 398
                     )
    paypal_express_checkout_tool = paypal_api_tools.PaypalExpressCheckout()
    paypal_express_checkout_tool.set_token_obj( pending_token )
    
    paypal_main.process_individual_payment( paypal_express_checkout_tool )