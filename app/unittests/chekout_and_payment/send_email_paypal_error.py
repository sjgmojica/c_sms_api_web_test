from gevent.monkey import patch_all
patch_all()
from tornado.options import define, options, parse_command_line, print_help
from features.configuration import Configuration


define("config", default='debug', help="run configuration settings", type=str)
define("local_settings", default="true", help="enable/disable use of local settings", type=str)


if __name__ == '__main__':


    parse_command_line()
    Configuration.initialize()
    
    values = Configuration.values()
    
    
    from features.paypal import paypal_main
    
    paypal_main.send_email_paypal_failed( to_='vagudelo@chikka.com', checkout_id=398 )